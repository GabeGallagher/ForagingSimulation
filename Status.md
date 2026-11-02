# Project Status

Where the project stands against the plan in [Readme.md](Readme.md).

---

## Current Implementation

What is built today. Where the implementation differs from the plan, it's noted inline.

### Running the Simulation
Entry point is `run_simulation.py`. Options are set at the top of its `__main__` block:
- `rand_sim` - `True` generates random obstacles (centers in 0.2-0.7 m, radii 0.025-0.2 m, overlap allowed) and saves the layout to `last_run_config.json` in the repo root, overwriting the previous one. `False` loads a saved layout.
- `saved_arena` - name (without `.json`) of the layout to load from `test_arenas/`, or `None` to replay the last random run
- `headless` - `True` runs 400 steps with no window
- `nav_type` - `NavType.POTENTIAL_FIELD` or `NavType.BASIC`

Arena layouts are JSON files with `target_locations` and `obstacle_specs` (`[x, y, radius]` per obstacle). Neither `test_arenas/` nor `last_run_config.json` is in version control. If the chosen layout file doesn't exist (as on a fresh clone), the script prints a notice and generates a random arena instead. To keep a random layout, copy `last_run_config.json` into `test_arenas/` under a new name.

Default timing: 50 ms simulation step, 20 fps rendering.

### Core Loop
- `SimulationManager` steps the world on a fixed time step in a background thread. Anything that needs per-step updates extends `TimeStepObserver` and subscribes automatically.
- Each step, all observers update first (the nest steers, bots move), then the `CollisionManager` resolves collisions. Physics always runs last, so no step ends with a bot inside a wall.
- `VisualizationManager` renders with matplotlib on the main thread. Space toggles pause.

### Arena
- 1m x 1m, circular obstacles from the layout file, any number of targets
- **Walls** are a `BoundaryCollider`. Anything movable that overlaps a wall is pushed back inside, so bots can touch or slide along a wall but never cross it. Bots, the bot interface, and the nest take no part in enforcing this. *(Plan said bots stop on wall contact; they slide instead.)*
- **Obstacles** are colliders but not yet solid. Navigation keeps bots out of them; physics does not.

### Collisions
- `CollisionManager` checks every pair of registered colliders each step (bots, nest, targets, obstacles, walls).
- Colliders are static by default; only bot colliders are `movable`. In a static/movable pair the static side reacts first, so a bot has already been pushed back by the time it's told it collided.
- Report path: `MicroBotCollider` -> `MicroBot.handle_collision` (sets `IDLE`) -> `BotInterface.report_collision` -> `Nest.handle_collision`. The nest re-steers on walls, obstacles, and other bots, collects on targets, and accepts delivery on contact with the nest while `RETURNING`.
- *(Divergence from plan: the collider object itself is passed up to the nest, so the nest knows what was hit and where, rather than inferring it from a collision timestamp.)*

### Bots
- 1 cm long, 20 cm/s constant speed, instant rotation; collision radius 0.5 cm
- States: `IDLE`, `EXPLORING`, `RETURNING` (`BLOCKED` exists but is unused)
- Currently one bot is spawned per run; each bot makes one trip and is removed when it delivers to the nest.

### Nest (Brain)
- **Spawning:** bots spawn at the nest center. If an obstacle is too close, the nest scans outward in rings (one bot radius apart, out to its 0.1 m radius) and uses the first point that clears every obstacle by the bot radius plus 1 cm and is inside the arena. If no such point exists, it raises an error.
- **Task assignment:** each bot is assigned one target, round-robin across bots, the first time it needs one, and keeps it. *(Plan said nearest unassigned target.)*
- **Stuck detection:** the nest records each bot's position every step. A bot that moves less than 2 cm net over 40 steps (2 s) is reported to the navigator as stuck.
- The nest is navigation-agnostic: it asks `self.nav.get_bot_direction(...)` for a heading without knowing which algorithm is in use.

### Navigation
All navigators extend `Navigation` (`get_direction`, plus an overridable `get_bot_direction` for per-bot behavior).

**`BASIC`** - deliberately minimal placeholder; steers straight at the target and is not expected to complete a trip.

**`POTENTIAL_FIELD`** - the bot's heading is the direction of the summed force:
- **Attraction** toward the target (or the nest when returning)
- **Obstacle repulsion** - Khatib's FIRAS form, `eta * (1/d - 1/d0) / d^2` where `d` is distance to the obstacle's surface. It grows without bound near the surface, so target and wall forces can never push a bot into an obstacle.
- **Circulation** - a tangential force on each obstacle, equal in strength to its repulsion, steering bots around the side facing the target. This removes the stall when bot, obstacle, and target are collinear, and helps bots pass through gaps between obstacles. Exactly collinear cases tie-break to a fixed side.
- **Escape** - if a bot is ever inside an obstacle, it heads straight out.
- **Wall repulsion** - linear and bounded, so bots can still travel along a wall.

**Boundary following (recovery)** - when the nest reports a bot as stuck, the potential field switches that bot to Bug-style boundary following:
- Track the nearest obstacle's edge at a fixed standoff, circling the same direction the field chose
- If following would drive into an arena wall, reverse once; a second wall ends the episode
- Return to the field once the bot is 5 cm closer to its target than where it got stuck, or if its target changes

Tuning parameters:

| Parameter | Where | Value | Meaning |
|---|---|---|---|
| `attractive_strength` | `PotentialField` | 0.2 | Pull toward the target |
| `influence_dist` | `PotentialField` | 0.2 m | Range of obstacle and wall repulsion |
| `beta` | `PotentialField` | 1 | Wall repulsion gain |
| `eta` | `PotentialField` | 1e-4 | Obstacle repulsion gain |
| `circulation` | `PotentialField` | 1.0 | Tangential force as a fraction of repulsion |
| `follow_standoff` | `PotentialField` | 0.025 m | Gap kept from an obstacle while boundary following; must be smaller than gaps bots should fit through |
| `follow_leave_margin` | `PotentialField` | 0.05 m | Progress toward the target needed to stop following |
| `radius` | `Nest` | 0.1 m | Nest size and spawn search radius |
| `spawn_margin` | `Nest` | 0.01 m | Spawn clearance beyond the bot radius |
| `stuck_window` | `Nest` | 40 steps | Window for stuck detection |
| `stuck_distance` | `Nest` | 0.02 m | Net movement below which a bot is stuck |

### Debug Tools
Overlay checkboxes in the visualization window: force vectors, headings, state colors, target lines, obstacle influence zones, and bot coordinates.

The force vector overlay draws one arrow per component the navigator used that step: attraction (blue), obstacle repulsion (red), circulation (orange), and walls (brown); or escape (black) or follow (teal) when those are steering instead. Arrow length scales with strength and is capped at 0.2 m, since repulsion grows without bound near an obstacle. The heading overlay shows the resulting direction. The navigator records components in `last_forces`, and the nest copies them to each bot's `debug_forces`.

### Known Limitations
- One bot per run
- Obstacles are not yet solid (planned to work like walls)
- The potential field's wall repulsion, the boundary follower's wall check, and the nest's spawn check all read the arena's bounds directly. These will need to change for the unknown-arena work in V2.
- Collected targets stay in `target_locations`, so with multiple bots a later bot could be assigned a target that's already gone
- If boundary following is blocked by walls in both directions, the bot falls back to the field, gets stuck again, and repeats
- The boundary follower's leave rule is simpler than Bug2 (closer to target only, not "back on the line to the target"), so it can leave a trap early

---

## Development Roadmap

Copied from [Readme.md](Readme.md) as a checklist. Items marked *partial* are started but don't yet meet the plan.

### Phase 1: Foundation (V1.0)
**Week 1-2:**
- [x] Build basic arena, bot, and physics
- [ ] Implement turn-and-move command system - *partial: the nest sets heading and bots move at constant speed, but there is no TURN/MOVE/TURNED command protocol*
- [x] Get single bot navigating to single target

**Week 3:**
- [ ] Add multiple bots (50) - *partial: one bot per run*
- [x] Implement brain task assignment - *round-robin, not nearest-unassigned*
- [ ] Get all bots collecting all targets

**Week 4:**
- [ ] Add energy accounting
- [x] Implement visualization
- [ ] Measure baseline performance

### Phase 2: Learning (V2.0)
**Week 5-6:**
- [ ] Remove brain's prior knowledge of layout
- [ ] Implement world model building
- [ ] Add exploration strategies

### Phase 3: Decentralization (V3.0)
**Week 7-9:**
- [ ] Implement local communication
- [ ] Design behavioral rules
- [ ] Remove centralized brain
- [ ] Compare centralized vs decentralized

### Phase 4: Complexity (V4.0)
**Week 10-12:**
- [ ] Multi-valued targets
- [ ] Cooperative transport
- [ ] Dynamic environments
- [ ] Robustness testing

### Phase 5: Publication/Portfolio
**Week 13+:**
- [ ] Document findings - *partial: ongoing in findings.md*
- [ ] Create comparison visualizations
- [ ] Write up research results
- [ ] Video demonstrations

---

## Research Deliverables

### Experimental Data
- [ ] Performance metrics for each version
- [ ] Centralized vs decentralized comparison
- [ ] Scalability analysis (varying swarm sizes)
- [ ] Robustness testing results

### Visualizations
- [ ] Videos of swarm behavior
- [ ] Graphs of energy efficiency
- [ ] Heatmaps of exploration coverage
- [ ] Comparison charts

### Documentation
- [x] This architecture document
- [ ] Code documentation - *partial: docstrings on some modules*
- [ ] Findings write-up - *partial: ongoing in findings.md*
- [ ] Lessons learned - *partial: ongoing in findings.md*

### Future Work
- [ ] Apply ML/RL to optimize strategies
- [ ] Build physical prototype (3-5 robots)
- [ ] Scale to larger swarms (1000+ bots)
- [ ] Apply to real problems (cleaning robots, microplastic capture)
