import os
import random
import pygame

pygame.init()

# Screen settings
WIDTH, HEIGHT = 1000, 1000
TILE_SIZE = 15
GRID_WIDTH = WIDTH // TILE_SIZE
GRID_HEIGHT = HEIGHT // TILE_SIZE

# Load terrain sprites
sprite_paths = {
    "normal_grass": os.path.join("Sprites", "normal_grass.png"),
    "cobble": os.path.join("Sprites", "cobble.png"),
    "brown_grass": os.path.join("Sprites", "brown_grass.png"),
    "red_grass": os.path.join("Sprites", "red_grass.png"),
    "flower_land": os.path.join("Sprites", "flower_land.png"),
    "hut": os.path.join("Sprites", "hut.png"),
    "castle": os.path.join("Sprites", "castle.png"),
    "goblin": os.path.join("Sprites", "goblin.png"),
    "mage": os.path.join("Sprites", "mage.png")
}

terrain_types = ["cobble", "brown_grass", "red_grass", "flower_land"]
terrain_sprites = {key: pygame.image.load(path) for key, path in sprite_paths.items()}

# Both buildings will be the same size - 3x3 tiles
BUILDING_SIZE = 3

# Special zones
GOBLIN_STRONGHOLD = "brown_grass"  # Brown grass is goblin territory
MAGE_BASE = "flower_land"         # Flower land is mage territory

# Game of Life settings
SIMULATION_SPEED = 2 # Frames between updates
simulation_counter = 0
paused = True  # Start paused

def scale_sprites():
    """Scales all terrain sprites to fit the grid."""
    global terrain_sprites
    
    # Scale all sprites to fit one tile
    for key, sprite in terrain_sprites.items():
        terrain_sprites[key] = pygame.transform.scale(sprite, (TILE_SIZE, TILE_SIZE))
    
    # Create larger versions of buildings (both same size)
    terrain_sprites["large_hut"] = pygame.transform.scale(
        terrain_sprites["hut"], 
        (TILE_SIZE * BUILDING_SIZE, TILE_SIZE * BUILDING_SIZE)
    )
    
    terrain_sprites["large_castle"] = pygame.transform.scale(
        terrain_sprites["castle"], 
        (TILE_SIZE * BUILDING_SIZE, TILE_SIZE * BUILDING_SIZE)
    )

scale_sprites()

from collections import deque

def generate_clustered_terrain():
    """Generates a clustered terrain map with multiple clusters per terrain type."""

    def is_cluster_large_enough(grid):
        """Check if all clusters meet the minimum size requirement."""
        MIN_CLUSTER_SIZE = {
            "cobble": 25,
            "red_grass": 25,
            "flower_land": 50,
            "brown_grass": 50
        }

        terrain_counts = {terrain: 0 for terrain in MIN_CLUSTER_SIZE.keys()}

        # Count terrain occurrences
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x] in terrain_counts:
                    terrain_counts[grid[y][x]] += 1

        # Check if all terrain types meet the required minimum size
        for terrain, min_size in MIN_CLUSTER_SIZE.items():
            if terrain_counts[terrain] < min_size:
                return False
        return True

    def generate():
        """Generates the terrain and clusters."""
        grid = [["normal_grass" for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        cluster_map = {}

        # Define terrain generation order
        terrain_order = [
            ["cobble", "red_grass"],
            ["brown_grass", "flower_land"]
        ]

        for tier in terrain_order:
            for terrain in tier:
                cluster_map[terrain] = []
                num_clusters = 1 if terrain in ["cobble", "red_grass"] else random.randint(2, 4)
                largest_cluster = None

                for _ in range(num_clusters):
                    start_x = random.randint(0, GRID_WIDTH - 1)
                    start_y = random.randint(0, GRID_HEIGHT - 1)

                    cluster_size = random.randint(50, 300)
                    stack = [(start_x, start_y)]
                    count = 0
                    cluster_positions = set()

                    while stack and count < cluster_size:
                        x, y = stack.pop()
                        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and grid[y][x] == "normal_grass":
                            grid[y][x] = terrain
                            cluster_positions.add((x, y))
                            count += 1

                            # Ensure connectivity
                            neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                            if count % 5 == 0:
                                neighbors += [(x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1)]

                            random.shuffle(neighbors)
                            stack.extend(n for n in neighbors if 0 <= n[0] < GRID_WIDTH and 0 <= n[1] < GRID_HEIGHT)

                    if len(cluster_positions) > 25:
                        if terrain in ["cobble", "red_grass"]:
                            if largest_cluster is None or len(cluster_positions) > len(largest_cluster):
                                largest_cluster = cluster_positions
                        else:
                            cluster_map[terrain].append(cluster_positions)

                if largest_cluster:
                    cluster_map[terrain] = [largest_cluster]

        return grid, cluster_map

    # Loop until the terrain satisfies the cluster size requirements
    grid, cluster_map = generate()
    while not is_cluster_large_enough(grid):
        grid, cluster_map = generate()

    # Post-processing: Remove isolated 1x1 or 2x2 spots for any terrain type
    for y in range(1, GRID_HEIGHT - 1):
        for x in range(1, GRID_WIDTH - 1):
            current_terrain = grid[y][x]
            terrain_counts = {}

            # Count surrounding terrain types
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
                neighbor = grid[y + dy][x + dx]
                terrain_counts[neighbor] = terrain_counts.get(neighbor, 0) + 1

            # If a terrain has 2 or fewer matching neighbors, convert it to the dominant surrounding terrain
            if terrain_counts.get(current_terrain, 0) <= 1:
                dominant_terrain = max(terrain_counts, key=terrain_counts.get)
                if terrain_counts[dominant_terrain] >= 6:
                    grid[y][x] = dominant_terrain

    # Post-processing: Fill in fully enclosed normal_grass patches
    def is_enclosed(x, y, grid, target_type):
        """Checks if a `normal_grass` patch is completely enclosed by a single terrain type."""
        queue = deque([(x, y)])
        visited = set()
        enclosed = True
        dominant_terrain = None

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))

            # Check bounds
            if cx == 0 or cy == 0 or cx == GRID_WIDTH - 1 or cy == GRID_HEIGHT - 1:
                enclosed = False  # Touching the edge means it's not enclosed

            # Scan neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    neighbor = grid[ny][nx]
                    if neighbor == target_type:
                        queue.append((nx, ny))
                    elif dominant_terrain is None:
                        dominant_terrain = neighbor  # First surrounding terrain
                    elif dominant_terrain != neighbor:
                        enclosed = False  # Different terrain types mean it's not fully enclosed

        return enclosed, dominant_terrain

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == "normal_grass":
                enclosed, dominant_terrain = is_enclosed(x, y, grid, "normal_grass")
                if enclosed and dominant_terrain:
                    grid[y][x] = dominant_terrain  # Convert fully enclosed patch

    return grid, cluster_map


def check_building_fit(x, y, terrain_type):
    """Check if a building can fit at the given position on the specified terrain."""
    if (x + BUILDING_SIZE > GRID_WIDTH or 
        y + BUILDING_SIZE > GRID_HEIGHT):
        return False
    
    # Check if all required tiles are of the right terrain
    for dx in range(BUILDING_SIZE):
        for dy in range(BUILDING_SIZE):
            if terrain_map[y + dy][x + dx] != terrain_type:
                return False
    
    return True

def place_buildings():
    """Places buildings on valid terrain (hut on red grass, castle on cobble)."""
    hut_pos = None
    castle_pos = None
    building_area = {}  # Track which tiles are occupied by buildings
    
    # Find a suitable location for the hut in red grass
    if "red_grass" in clusters and clusters["red_grass"]:
        # Sort clusters by size (largest first) to find good candidates
        valid_red_clusters = sorted(clusters["red_grass"], key=len, reverse=True)
        
        for cluster in valid_red_clusters:
            # Convert to list for random sampling
            cluster_list = list(cluster)
            # Try random positions until we find one that fits
            random.shuffle(cluster_list)
            
            for x, y in cluster_list:
                if check_building_fit(x, y, "red_grass"):
                    hut_pos = (x, y)
                    # Mark area as occupied
                    building_area["hut"] = {(x+dx, y+dy) for dx in range(BUILDING_SIZE) for dy in range(BUILDING_SIZE)}
                    break
            
            if hut_pos:
                break
    
    # Find a suitable location for the castle in cobble
    if "cobble" in clusters and clusters["cobble"]:
        valid_cobble_clusters = sorted(clusters["cobble"], key=len, reverse=True)
        
        for cluster in valid_cobble_clusters:
            cluster_list = list(cluster)
            random.shuffle(cluster_list)
            
            for x, y in cluster_list:
                if check_building_fit(x, y, "cobble"):
                    castle_pos = (x, y)
                    # Mark area as occupied
                    building_area["castle"] = {(x+dx, y+dy) for dx in range(BUILDING_SIZE) for dy in range(BUILDING_SIZE)}
                    break
            
            if castle_pos:
                break
    
    return hut_pos, castle_pos, building_area

def initialize_life_grid():
    """Initialize the game of life grid with some goblins and mages."""
    # Empty grid (None = empty)
    new_life_grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    # Place some initial goblins and mages
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            # Skip building areas
            if (j, i) in building_area.get("hut", set()) or (j, i) in building_area.get("castle", set()):
                continue
            
            # Random initial population with higher odds near their respective zones
            terrain = terrain_map[i][j]
            if terrain == GOBLIN_STRONGHOLD and random.random() < 0.3:
                new_life_grid[i][j] = "goblin"
            elif terrain == MAGE_BASE and random.random() < 0.3:
                new_life_grid[i][j] = "mage"
            # Sparser population in neutral territories
            elif random.random() < 0.05:
                new_life_grid[i][j] = random.choice(["goblin", "mage"])
    
    return new_life_grid

def count_neighbors(grid, row, col, cell_type):
    """Count number of neighbors of specified type."""
    count = 0
    for i in range(max(0, row-1), min(GRID_HEIGHT, row+2)):
        for j in range(max(0, col-1), min(GRID_WIDTH, col+2)):
            if (i != row or j != col) and grid[i][j] == cell_type:
                count += 1
    return count

def update_life_grid():
    """Update the game of life grid according to the terrain-specific rules."""
    global life_grid
    new_grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    conflicts = []
    
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            # Skip building areas
            if (j, i) in building_area.get("hut", set()) or (j, i) in building_area.get("castle", set()):
                continue

            terrain = terrain_map[i][j]
            goblin_count = count_neighbors(life_grid, i, j, "goblin")
            mage_count = count_neighbors(life_grid, i, j, "mage")
            cell = life_grid[i][j]
            
            # --- Normal Zone: normal_grass (green grass) ---
            if terrain == "normal_grass":
                if cell is None:
                    # Reproduction: spawn only if exactly 3 neighbors of one type exist.
                    if goblin_count == 3 and mage_count != 3:
                        new_grid[i][j] = "goblin"
                    elif mage_count == 3 and goblin_count != 3:
                        new_grid[i][j] = "mage"
                    elif goblin_count == 3 and mage_count == 3:
                        conflicts.append((i, j, goblin_count, mage_count))
                else:
                    if cell == "goblin":
                        new_grid[i][j] = "goblin" if goblin_count in (2, 3) else None
                    elif cell == "mage":
                        new_grid[i][j] = "mage" if mage_count in (2, 3) else None

            # --- Goblin Base: red_grass ---
            elif terrain == "red_grass":
                if cell is None:
                    # Reproduction: goblins spawn with exactly 2 neighbors (strong reproduction),
                    # mages spawn only if exactly 3 mage neighbors.
                    if goblin_count == 2 and mage_count != 3:
                        new_grid[i][j] = "goblin"
                    elif mage_count == 3 and goblin_count != 2:
                        new_grid[i][j] = "mage"
                    elif goblin_count == 2 and mage_count == 3:
                        conflicts.append((i, j, goblin_count, mage_count))
                else:
                    if cell == "goblin":
                        # Goblins survive with 2 or 3 neighbors (as in normal zone).
                        new_grid[i][j] = "goblin" if goblin_count in (2, 3) else None
                    elif cell == "mage":
                        # Mages survive only with exactly 3 or 4 mage neighbors.
                        new_grid[i][j] = "mage" if mage_count in (3, 4) else None

            # --- Mage Base: cobble ---
            elif terrain == "cobble":
                if cell is None:
                    # Reproduction: goblins spawn with exactly 4 neighbors,
                    # mages spawn with exactly 3 neighbors.
                    if goblin_count == 4 and mage_count != 3:
                        new_grid[i][j] = "goblin"
                    elif mage_count == 3 and goblin_count != 4:
                        new_grid[i][j] = "mage"
                    elif goblin_count == 4 and mage_count == 3:
                        conflicts.append((i, j, goblin_count, mage_count))
                else:
                    if cell == "goblin":
                        # Goblins use normal survival (2 or 3 neighbors) on mage base.
                        new_grid[i][j] = "goblin" if goblin_count in (2, 3) else None
                    elif cell == "mage":
                        # Magicians survive if they have between 2 and 5 mage neighbors.
                        new_grid[i][j] = "mage" if 2 <= mage_count <= 5 else None

            # --- Deadly Zone: brown_grass ---
            elif terrain == "brown_grass":
                if cell is None:
                    # If both goblins and mages try to expand to the same empty cell, do not populate it.
                    if goblin_count == 3 and mage_count == 3:
                        conflicts.append((i, j, goblin_count, mage_count))
                    # Normal reproduction: Spawn if exactly 3 neighbors of one type exist.
                    elif goblin_count == 3 and mage_count != 3:
                        new_grid[i][j] = "goblin"
                    elif mage_count == 3 and goblin_count != 3:
                        new_grid[i][j] = "mage"
                
                else:
                    # Only consider same-type neighbors for survival
                    same_type_neighbors = goblin_count if cell == "goblin" else mage_count

                    # Overcrowding: Dies if it has 4 or more same-type neighbors
                    if same_type_neighbors >= 4:
                        new_grid[i][j] = None
                    # Isolation: Dies if it has fewer than 3 same-type neighbors
                    elif same_type_neighbors < 3:
                        new_grid[i][j] = None
                    else:
                        # Conflict resolution if both goblins and mages are nearby
                        if goblin_count > 0 and mage_count > 0:
                            if goblin_count > mage_count:
                                new_grid[i][j] = "goblin"
                            elif mage_count > goblin_count:
                                new_grid[i][j] = "mage"
                            else:
                                new_grid[i][j] = cell  # Keep the existing occupant if equal allies
                        else:
                            new_grid[i][j] = cell  # Maintain the cell's current state if no rival conflict

            # --- Peaceful Zone: flower_land ---
            elif terrain == "flower_land":
                alive_neighbors = goblin_count + mage_count  # Count all alive cells regardless of type

                if cell is None:
                    # Spawn a random mob if exactly 3 alive neighbors exist
                    if alive_neighbors == 3:
                        new_grid[i][j] = random.choice(["goblin", "mage"])
                else:
                    # Survival rules based on total alive neighbors
                    if alive_neighbors < 2 or alive_neighbors > 4:
                        new_grid[i][j] = None  # Dies due to isolation or overpopulation
                    else:
                        new_grid[i][j] = cell  # Survives

            # --- Default: Other terrain uses normal rules ---
            else:
                if cell is None:
                    if goblin_count == 3 and mage_count != 3:
                        new_grid[i][j] = "goblin"
                    elif mage_count == 3 and goblin_count != 3:
                        new_grid[i][j] = "mage"
                    elif goblin_count == 3 and mage_count == 3:
                        conflicts.append((i, j, goblin_count, mage_count))
                else:
                    if cell == "goblin":
                        new_grid[i][j] = "goblin" if goblin_count in (2, 3) else None
                    elif cell == "mage":
                        new_grid[i][j] = "mage" if mage_count in (2, 3) else None

    # --- Conflict resolution ---
    for row, col, g_count, m_count in conflicts:
        if g_count > m_count:
            new_grid[row][col] = "goblin"
        elif m_count > g_count:
            new_grid[row][col] = "mage"
        else:
            new_grid[row][col] = None

    life_grid = new_grid



def draw_everything():
    """Draw the terrain, buildings, and life cells."""
    # First draw terrain
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            # Always draw the terrain layer
            screen.blit(terrain_sprites[terrain_map[row][col]], (col * TILE_SIZE, row * TILE_SIZE))
            
            # Draw life cells on top
            if life_grid[row][col] == "goblin":
                screen.blit(terrain_sprites["goblin"], (col * TILE_SIZE, row * TILE_SIZE))
            elif life_grid[row][col] == "mage":
                screen.blit(terrain_sprites["mage"], (col * TILE_SIZE, row * TILE_SIZE))
    
    # Draw buildings last (on top)
    if hut_pos:
        screen.blit(terrain_sprites["large_hut"], 
                   (hut_pos[0] * TILE_SIZE, hut_pos[1] * TILE_SIZE))
    
    if castle_pos:
        screen.blit(terrain_sprites["large_castle"], 
                   (castle_pos[0] * TILE_SIZE, castle_pos[1] * TILE_SIZE))
    
    # Draw game status
    font = pygame.font.SysFont('Arial', 24)
    status_text = "PAUSED" if paused else "RUNNING"
    text_surface = font.render(status_text, True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))
    
    # Draw instructions
    instructions = [
        "SPACE: Pause/Resume",
        "R: Reset terrain",
        "C: Clear life grid",
        "G: Add goblins",
        "M: Add mages"
    ]
    
    for idx, instruction in enumerate(instructions):
        text_surface = font.render(instruction, True, (255, 255, 255))
        screen.blit(text_surface, (10, 40 + idx * 30))

def add_random_entities(entity_type, count=50):
    """Add random entities of given type to the life grid."""
    added = 0
    
    while added < count:
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        
        # Skip building areas
        if (x, y) in building_area.get("hut", set()) or (x, y) in building_area.get("castle", set()):
            continue
        
        # Add entity if space is empty
        if life_grid[y][x] is None:
            life_grid[y][x] = entity_type
            added += 1

# Generate the terrain
terrain_map, clusters = generate_clustered_terrain()

# Place buildings on the terrain
hut_pos, castle_pos, building_area = place_buildings()

# Initialize life grid
life_grid = initialize_life_grid()

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Goblin vs Mage Game of Life")
clock = pygame.time.Clock()
running = True

# Main game loop
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Toggle pause
                paused = not paused
            elif event.key == pygame.K_r:
                # Regenerate terrain and reset
                terrain_map, clusters = generate_clustered_terrain()
                hut_pos, castle_pos, building_area = place_buildings()
                life_grid = initialize_life_grid()
            elif event.key == pygame.K_c:
                # Clear life grid
                life_grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
            elif event.key == pygame.K_g:
                # Add random goblins
                add_random_entities("goblin")
            elif event.key == pygame.K_m:
                # Add random mages
                add_random_entities("mage")
        
        # Mouse interaction to add entities
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x, grid_y = mouse_x // TILE_SIZE, mouse_y // TILE_SIZE
            
            # Left click adds goblin, right click adds mage
            if event.button == 1:  # Left click
                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                    if (grid_x, grid_y) not in building_area.get("hut", set()) and (grid_x, grid_y) not in building_area.get("castle", set()):
                        life_grid[grid_y][grid_x] = "goblin"
            elif event.button == 3:  # Right click
                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                    if (grid_x, grid_y) not in building_area.get("hut", set()) and (grid_x, grid_y) not in building_area.get("castle", set()):
                        life_grid[grid_y][grid_x] = "mage"
    
    # Update simulation
    if not paused:
        simulation_counter += 1
        if simulation_counter >= SIMULATION_SPEED:
            update_life_grid()
            simulation_counter = 0
    
    # Draw everything
    screen.fill((0, 0, 0))
    draw_everything()
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()