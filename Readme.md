# Foraging Swarm Simulation - Architecture Document

## Project Overview

**Goal:** Build a simulation of autonomous micro-robots doing collective foraging to learn swarm intelligence, coordination strategies, and compare centralized vs decentralized control paradigms.

**Research Questions:**
- What coordination strategies work best for different problems?
- How does centralized vs decentralized control affect performance?
- What's the minimal sensing required for effective foraging?
- How does swarm size affect performance and scalability?

---

## Version 1.0 - Basic Foraging (Centralized, Perfect Information)

### Scope
Single target retrieval with known environment layout. Focus on getting basic coordination working.

### Arena Specification
- **Size:** 1m × 1m square
- **Walls:** Solid boundaries (bots stop on collision)
- **Obstacles:** 5 circular obstacles, 10cm radius, random positions
- **Nest:** Located in one corner (e.g., 0.1, 0.1)
- **Targets:** 3 targets at random positions
- **Rendering:** Top-down 2D view

### Bot Specification
- **Quantity:** 50 bots
- **Size:** 1cm diameter (spherical)
- **Sensing:** Touch only - no vision, no distance sensing
- **Movement:** Constant speed, instant rotation
- **Starting Position:** All bots start at nest
- **State Machine:**
  - IDLE: Waiting for command
  - TURNING: Executing rotation (instant)
  - MOVING: Moving forward until collision
  - REPORTING: Sending event to brain

### Bot Capabilities
**Knowledge:**
- Current heading (angle bot is facing)
- Last command received

**Actions:**
- Execute `TURN(angle)` - instantly rotate to new heading
- Execute `MOVE()` - move forward at constant speed until collision
- Detect collision via touch
- Report events to brain

**Does NOT know:**
- Absolute position (x, y)
- What type of object was hit
- Distance to anything
- Other bots' states

### Bot Command Interface
**Commands (Brain → Bot):**
- `TURN(angle)` - set new heading (degrees, absolute)
- `MOVE()` - move forward until collision
- `STOP()` - halt movement (optional, for emergencies)

**Reports (Bot → Brain):**
- `TURNED()` - turn completed successfully
- `COLLISION(timestamp)` - hit something at this time
- `ARRIVED_AT_NEST()` - special case when reaching nest with target

### Brain Specification
- **Architecture:** Centralized controller
- **Position Tracking:** Perfect knowledge (reads from simulation)
- **World Model:** Static 2D grid/map, knows all obstacle and target positions upfront
- **Navigation:** Simple potential field or direct pathfinding (A*, straight line)
- **Task Assignment:** Assigns nearest unassigned target to available bots

### Brain Capabilities
**Knowledge:**
- Exact position (x, y, heading) of every bot at all times
- Complete arena layout (obstacles, walls, nest, targets)
- Which targets have been collected
- Which bots are carrying targets

**Responsibilities:**
- Track bot positions (reads from simulation)
- Assign tasks to bots (which target to retrieve)
- Calculate navigation paths
- Determine what object bot collided with (based on collision position)
- Issue turn and move commands
- Update task status (target collected, bot returned)

### Physics Model
- **Movement:** Overdamped motion (no inertia)
- **Speed:** Constant velocity for all bots
- **Collisions:** Bots stop on contact with any object
- **Time Step:** Synchronous updates (all bots update each frame)

### Control Flow (Single Bot Cycle)
1. **Brain** calculates desired heading for bot toward target
2. **Brain** sends `TURN(angle)` command
3. **Bot** rotates instantly to new heading
4. **Bot** sends `TURNED()` report
5. **Brain** sends `MOVE()` command
6. **Bot** moves forward at constant speed
7. **Bot** collides with something (obstacle/target/wall/other bot)
8. **Bot** sends `COLLISION(timestamp)` report and stops
9. **Brain** calculates collision position: `start_pos + (velocity × time)`
10. **Brain** checks what's at collision position
11. **Brain** decides next action:
    - If target: Issue pickup and return-to-nest commands
    - If obstacle: Recalculate path around obstacle
    - If wall/bot: Redirect to avoid

### Success Metrics (Energy-Based)
**Energy Accounting:**
- Each target has energy value (e.g., 100 units)
- Movement costs energy (proportional to distance traveled)
- Idling costs energy (small constant per timestep)
- Collisions cost extra energy (damage/recovery cost)

**Primary Metric:** Energy efficiency ratio
```
efficiency = (total energy collected) / (total energy spent)
```

**Secondary Metrics:**
- Time to collect all targets
- Total distance traveled by all bots
- Number of collisions
- Percentage of arena explored

**Survival Constraint:**
- Swarm starts with initial energy reserve
- Must collect targets before reserve depleted
- Prevents "do nothing" degenerate strategy

### Termination Conditions
- **Success:** All targets collected and returned to nest
- **Failure:** Swarm energy depleted before all targets collected
- **Timeout:** Maximum simulation time reached (partial success)

### UI Requirements
**Visualization:**
- Top-down 2D view
- Bots rendered as colored dots
- Targets as stars
- Obstacles as gray circles
- Nest as distinct marker
- Optional: trail paths showing bot movement history

**Controls:**
- Start/pause/reset simulation
- Speed control (fast-forward)
- Step-by-step mode for debugging

**Data Display:**
- Current energy reserves
- Targets collected / remaining
- Simulation time
- Real-time energy efficiency

---

## Version 2.0 - Unknown Environment (Centralized, Learning)

### Changes from V1
**Brain starts blind:**
- Knows arena dimensions and nest location
- Does NOT know obstacle positions
- Does NOT know target positions

**World Model Building:**
- Brain maintains 2D occupancy grid
- Updates cells as: UNKNOWN → OBSTACLE or CLEAR or TARGET
- Uses bot collision reports to discover environment

**Exploration Strategy:**
- Systematic grid search, OR
- Random walk exploration, OR
- Frontier-based exploration (explore boundaries of known space)

**New Metrics:**
- Time to discover all targets
- Exploration efficiency (area covered / distance traveled)
- Map accuracy (brain's model vs actual environment)

---

## Version 3.0 - Decentralized Swarm Intelligence

### Major Architectural Change
**Remove centralized brain** - bots coordinate via local rules only.

### Bot Changes
**Enhanced Capabilities:**
- Local communication (can share info with bots within communication radius)
- Simple memory (remember last N positions/events)
- Local decision-making (choose direction based on local rules)

**Communication Model:**
- Each bot has communication range (e.g., 20cm radius)
- Can broadcast messages to nearby bots
- Messages: "Target at direction θ", "Obstacle ahead", "Follow me"

**Behavioral Rules (examples):**
- **Exploration:** Random walk or Lévy flight
- **Recruitment:** When target found, broadcast signal
- **Following:** Move toward bots signaling target discovery
- **Obstacle avoidance:** Turn away from collision
- **Return to nest:** Use path integration (track vector to nest)

### Pheromone System (Optional)
**Virtual pheromones in environment:**
- Bots deposit pheromone trails when successful
- Other bots follow pheromone gradients
- Pheromones decay over time
- Different pheromone types: "to target", "to nest", "danger"

### No Central Brain
- No global position tracking
- No task assignment
- No centralized pathfinding
- Coordination emerges from local interactions

### Comparison Study
Run same scenarios with V2 (centralized) and V3 (decentralized):
- Which performs better in different environments?
- How does scalability differ? (100 vs 500 vs 1000 bots)
- Robustness to bot failures?
- Energy efficiency comparison?

---

## Version 4.0 - Advanced Features

### Multi-Target Values
- Targets have different energy values (small/medium/large)
- Brain/swarm must prioritize high-value targets

### Weighted Targets (Multi-Bot Required)
- Some targets too heavy for single bot
- Requires 2-5 bots to cooperate
- Coordination challenge: rendezvous at target, synchronized transport

**New Bot Capability:**
- `ATTACH_TO_TARGET()` - wait at target for other bots
- `LIFT()` - collectively move target
- `DETACH()` - release target at nest

### Dynamic Environment
- Targets spawn/despawn during simulation
- UI allows manual placement/removal of targets
- Tests adaptability of swarm

### Obstacles with Variation
- Different sizes (5cm to 30cm radius)
- Different shapes (rectangles, irregular polygons)
- Moving obstacles or "predators" that chase bots

### Bot Failures
- Random bots "die" during simulation (removed from swarm)
- Tests robustness of coordination strategy
- Remaining bots must adapt

---

## Version 5.0 - 3D Extension (Long-term)

### Environment
- 3D arena (cube or sphere)
- Targets at different heights
- Aerial/underwater swarm simulation

### Bot Changes
- 3D position and orientation
- Pitch and yaw in addition to heading
- Gravity or buoyancy forces

### Visualization
- 3D rendering
- Camera controls (rotate, zoom, pan)

**Note:** Stay in 2D for extended period. Most concepts transfer from 2D → 3D. Only pursue 3D when specifically needed for research questions about vertical space.

---

## Implementation Architecture (All Versions)

### Clean Separation of Concerns

**Module 1: Physics/Simulation**
- Handles position updates
- Collision detection
- Movement integration
- Time stepping

**Module 2: Bot**
- Executes commands (turn, move)
- Detects collisions
- Reports events
- Minimal logic

**Module 3: Brain/Controller**
- Decision-making (centralized versions)
- Position tracking
- Task assignment
- Pathfinding

**Module 4: Communication**
- Bot ↔ Brain messaging
- Bot ↔ Bot messaging (decentralized versions)
- Event queue

**Module 5: Visualization/UI**
- Rendering
- User controls
- Data displays
- Recording/replay

**Module 6: Metrics/Analysis**
- Energy accounting
- Performance measurement
- Data logging
- Comparison tools

### Key Design Principles

**Pluggable Components:**
- Easy to swap centralized brain for decentralized rules
- Easy to swap perfect positioning for dead reckoning
- Easy to swap exploration strategies

**Clear Interfaces:**
- Bot command interface (TURN, MOVE, STOP)
- Bot report interface (TURNED, COLLISION, etc.)
- Brain query interface (get_position, assign_task)

**Data Logging:**
- Record every event for replay and analysis
- Export metrics to CSV for plotting
- Save world state for resuming simulations

---

## Development Roadmap

### Phase 1: Foundation (V1.0)
**Week 1-2:**
- Build basic arena, bot, and physics
- Implement turn-and-move command system
- Get single bot navigating to single target

**Week 3:**
- Add multiple bots (50)
- Implement brain task assignment
- Get all bots collecting all targets

**Week 4:**
- Add energy accounting
- Implement visualization
- Measure baseline performance

### Phase 2: Learning (V2.0)
**Week 5-6:**
- Remove brain's prior knowledge of layout
- Implement world model building
- Add exploration strategies

### Phase 3: Decentralization (V3.0)
**Week 7-9:**
- Implement local communication
- Design behavioral rules
- Remove centralized brain
- Compare centralized vs decentralized

### Phase 4: Complexity (V4.0)
**Week 10-12:**
- Multi-valued targets
- Cooperative transport
- Dynamic environments
- Robustness testing

### Phase 5: Publication/Portfolio
**Week 13+:**
- Document findings
- Create comparison visualizations
- Write up research results
- Video demonstrations

---

## Research Deliverables

### Experimental Data
- Performance metrics for each version
- Centralized vs decentralized comparison
- Scalability analysis (varying swarm sizes)
- Robustness testing results

### Visualizations
- Videos of swarm behavior
- Graphs of energy efficiency
- Heatmaps of exploration coverage
- Comparison charts

### Documentation
- This architecture document
- Code documentation
- Findings write-up
- Lessons learned

### Future Work
- Apply ML/RL to optimize strategies
- Build physical prototype (3-5 robots)
- Scale to larger swarms (1000+ bots)
- Apply to real problems (cleaning robots, microplastic capture)

---

## Notes and Considerations

### Dead Reckoning Evolution
- V1: Perfect position tracking (brain reads from simulation)
- V2: Brain estimates positions from commands (accumulates error)
- V3: No global positions, only local awareness

### Sensing Evolution
- V1: Touch only
- Later: Add distance sensors (proximity detection)
- Later: Add vision (detect objects at range)
- Later: Add communication sensors (hear broadcasts)

### Collision Handling Edge Cases
- Bot trapped in corner (detect stuck state)
- Two bots colliding (both report, brain resolves)
- Bot hitting wall repeatedly (redirect strategy)
- Bot-target collision (successful pickup)

### Parameter Tuning
Key parameters to experiment with:
- Number of bots (50 → 100 → 500)
- Bot speed (constant initially, vary later)
- Communication range (for decentralized)
- Energy costs (movement, idle, collision)
- Pheromone decay rate (for stigmergy)

### Debugging Tools
- Step-by-step execution
- Position history visualization
- Energy budget breakdown
- Bot state inspection
- Event log viewer