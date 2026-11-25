import pygame
import random
import math
import sys
import asyncio

async def main():

    pygame.init()

    WIDTH = 752
    HEIGHT = 750
    GRID_COLS = 25
    GRID_ROWS = 20
    CELL_SIZE = min(WIDTH // GRID_COLS, (HEIGHT - 150) // GRID_ROWS)
    FPS = 60

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("maze game yay")
    clock = pygame.time.Clock()

    #fonts
    font_default = pygame.font.Font(None, 25)

    #images
    player_image = pygame.image.load("assets/fish.png").convert_alpha()
    coral_collect_image = pygame.image.load("assets/coral.png").convert_alpha()
    algae_collect_image = pygame.image.load("assets/algae.png").convert_alpha()
    turtle_npc_image = pygame.image.load("assets/turtle.png").convert_alpha()
    turtle_npc_angy_image = pygame.image.load("assets/turtle_any.png").convert_alpha()
    pufferfish_npc_image = pygame.image.load("assets/pufferfish.png").convert_alpha()
    pufferfish_npc_angy_image = pygame.image.load("assets/puffer_angy.png").convert_alpha()
    fuel_harm_image = pygame.image.load("assets/fuelity.png").convert_alpha()
    npc_radius = pygame.image.load("assets/rad.png").convert_alpha()
    fire = pygame.image.load("assets/fire.png").convert_alpha()
    menu = pygame.image.load("assets/menu.png").convert_alpha()
    endGame_image = pygame.image.load("assets/endgame.png").convert_alpha()
    gameComplete_image = pygame.image.load("assets/complete.png").convert_alpha()
    trap_image = pygame.image.load("assets/trap.png").convert_alpha()

    player_image = pygame.transform.scale(player_image, (18, 18))
    coral_collect_image = pygame.transform.scale(coral_collect_image, (18, 18))
    algae_collect_image = pygame.transform.scale(algae_collect_image, (18, 18))
    turtle_npc_image = pygame.transform.scale(turtle_npc_image, (18, 18))
    turtle_npc_angy_image = pygame.transform.scale(turtle_npc_angy_image, (18, 18))
    pufferfish_npc_image = pygame.transform.scale(pufferfish_npc_image, (18, 18))
    pufferfish_npc_angy_image = pygame.transform.scale(pufferfish_npc_angy_image, (18, 18))
    fuel_harm_image = pygame.transform.scale(fuel_harm_image, (14, 14))
    npc_radius = pygame.transform.scale(npc_radius, (50, 50))
    fire = pygame.transform.scale(fire, (30, 30))
    menu = pygame.transform.scale(menu, (752, 750))
    endGame_image = pygame.transform.scale(endGame_image, (752, 750))
    gameComplete_image = pygame.transform.scale(gameComplete_image, (752, 750))
    trap_image = pygame.transform.scale(trap_image, (260, 90))

    #maze generation-------------------------------------------------------------------------------------------
    class Cell:
        def __init__(self, row, col):
            self.row = row
            self.col = col
            self.walls = {"top": True, "bottom": True, "right": True, "left": True}
            self.is_visited = False

        def draw(self, screen):
            x = self.col * CELL_SIZE
            y = self.row * CELL_SIZE
            wall_color = (255, 255, 255)
            pygame.draw.rect(screen, (135, 235, 255), ((GRID_COLS - 1) * CELL_SIZE, (GRID_ROWS - 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            if self.walls["top"]:
                pygame.draw.line(screen, wall_color, (x, y), (x + CELL_SIZE, y), 2)
            if self.walls["bottom"]:
                pygame.draw.line(screen, wall_color, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)
            if self.walls["right"]:
                pygame.draw.line(screen, wall_color, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
            if self.walls["left"]:
                pygame.draw.line(screen, wall_color, (x, y), (x, y + CELL_SIZE), 2)

        def find_neighbors(self, grid):
            neighbors = []
            directions = [("top", 0, -1), ("bottom", 0, 1), ("right", 1, 0), ("left", -1, 0)]
            for direction, dx, dy in directions:
                new_row = self.row + dy
                new_col = self.col + dx
                if 0 <= new_row < GRID_ROWS and 0 <= new_col < GRID_COLS:
                    neighbor = grid[new_row][new_col]
                    if not neighbor.is_visited:
                        neighbors.append(neighbor)
            if neighbors:
                return random.choice(neighbors)
            else:
                return None

    def remove_walls(current_cell, next_cell):
        dx = current_cell.col - next_cell.col
        if dx == 1:
            current_cell.walls["left"] = False
            next_cell.walls["right"] = False
        elif dx == -1:
            current_cell.walls["right"] = False
            next_cell.walls["left"] = False
        dy = current_cell.row - next_cell.row
        if dy == 1:
                current_cell.walls["top"] = False
                next_cell.walls["bottom"] = False
        elif dy == -1:
            current_cell.walls["bottom"] = False
            next_cell.walls["top"] = False

    def generate_maze():
        stack = []
        current_cell = grid[0][0]
        current_cell.is_visited = True
        while True:
            next_cell = current_cell.find_neighbors(grid)
            if next_cell:
                next_cell.is_visited = True
                stack.append(current_cell)
                remove_walls(current_cell, next_cell)
                current_cell = next_cell
            elif stack:
                current_cell = stack.pop()
            else:
                break
        for i in range(GRID_COLS):
            grid[GRID_ROWS - 1][i].walls["bottom"] = True
        for i in range(GRID_ROWS):
            grid[i][GRID_COLS - 1].walls["right"] = True

    grid = [[Cell(y, x) for x in range(GRID_COLS)] for y in range(GRID_ROWS)]
    generate_maze()

    #player-----------------------------------------------------------------------------------------------------
    class Player:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.attacking = False
            self.image = player_image
            self.attack_timer = 0

        def attack(self):
            self.attacking = True
            self.attack_timer = 20
            self.hit_this_attack = False

        def update(self):
            if self.attack_timer > 0:
                self.attack_timer -= 1
            else:
                self.attacking = False

        def moveCells(self, dx, dy, grid):
            current_position = grid[self.y][self.x]
            if dx == 1 and not current_position.walls["right"]:
                self.x += 1
            if dx == -1 and not current_position.walls["left"]:
                self.x -= 1
            if dy == 1 and not current_position.walls["bottom"]:
                self.y += 1
            if dy == -1 and not current_position.walls["top"]:
                self.y -= 1

        def draw(self):
            center_x = (self.x * CELL_SIZE) + (CELL_SIZE // 2)
            center_y = (self.y * CELL_SIZE) + (CELL_SIZE // 2)
            if self.attacking:
                screen.blit(fire, (center_x, center_y - 10))
            screen.blit(self.image, (center_x - 8, center_y - 8))
    fish = Player()

    #game objects-----------------------------------------------------------------------------------------------
    CORAL_COLLECTED = 0
    ALGAE_COLLECTED = 0
    class gameObjects():
        def __init__(self, type):
            self.x = random.randint(1, GRID_COLS - 1)
            self.y = random.randint(1, GRID_ROWS - 1)
            if type == "coral":
                self.image = coral_collect_image
            if type == "algae":
                self.image = algae_collect_image
            if type == "fuelity":
                self.image = fuel_harm_image

        def draw(self):
            center_x = (self.x * CELL_SIZE) + (CELL_SIZE // 2)
            center_y = (self.y * CELL_SIZE) + (CELL_SIZE // 2)
            screen.blit(self.image, (center_x - 8, center_y - 8))

    corals = []
    for i in range(20):
        coral_obj = gameObjects("coral")
        corals.append(coral_obj)

    algaes = []
    for i in range(10):
        algae_obj = gameObjects("algae")
        algaes.append(algae_obj)

    fuels = []
    for i in range(10):
        fuel_obj = gameObjects("fuelity")
        fuels.append(fuel_obj)

    def isCollected():
        nonlocal CORAL_COLLECTED, ALGAE_COLLECTED, isTrapped
        for c in corals:
            if fish.x == c.x and fish.y == c.y:
                CORAL_COLLECTED += 1
                corals.remove(c)
        for a in algaes:
            if fish.x == a.x and fish.y == a.y:
                ALGAE_COLLECTED += 1
                algaes.remove(a)
        for f in fuels:
            if fish.x == f.x and fish.y == f.y:
                isTrapped = True
                fuels.remove(f)

    #NPC--------------------------------------------------------------------------------------------------------
    pufferfish_health = 3
    debug_Mode = False
    trap_timer = 0
    class NPC():
        def __init__(self, animal):
            self.x = random.randint(10, GRID_COLS - 1)
            self.y = random.randint(10, GRID_ROWS - 1)
            self.timer = 0
            self.goal = None
            self.path = []
            self.path_index = 1
            self.state = "patrol"
            self.a = animal
            if animal == "turtle":
                self.image = turtle_npc_image
            if animal == "puffer":
                self.image = pufferfish_npc_image

        def isHit(self, grid, player):
            m_distance = abs(self.x - player.x) + abs(self.y - player.y)
            if m_distance < 4 and player.attacking == True:
                return True

        def move(self, grid, goal):
            start = (self.x, self.y)
            stack = [start]
            visited = {start}
            parent = {start: None}

            directions = [
                (0, -1, "top"),
                (0, 1, "bottom"),
                (1, 0, "right"),
                (-1, 0, "left")]

            while stack:
                current = stack.pop()
                if current == goal:
                    path = []
                    while current is not None:
                        path.append(current)
                        current = parent[current]
                    self.path = path[::-1]
                    self.path_index = 1
                    return
                x, y = current
                for dx, dy, direction in directions:
                    nx = x + dx
                    ny = y + dy
                    if (0 <= nx < GRID_COLS and
                        0 <= ny < GRID_ROWS and
                        not grid[y][x].walls[direction] and
                        (nx, ny) not in visited):
                        neighbor = (nx, ny)
                        visited.add(neighbor)
                        parent[neighbor] = current
                        stack.append(neighbor)
            self.path = []
            self.path_index = 1

        def update(self, grid, player):
            m_distance = abs(self.x - player.x) + abs(self.y - player.y)
            if m_distance <= 10:
                self.state = "attack"
                if self.a == "puffer":
                    self.image = pufferfish_npc_angy_image
                if self.a == "turtle":
                    pass
            else:
                self.state = "patrol"
                if self.a == "puffer":
                    self.image = pufferfish_npc_image
                if self.a == "turtle":
                    pass
        
            if self.state == "patrol":
                if self.goal is None or self.path_index >= len(self.path):
                    n_goal_x = random.randint(0, GRID_COLS - 1)
                    n_goal_y = random.randint(0, GRID_ROWS - 1)
                    self.goal = (n_goal_x, n_goal_y)
                    self.move(grid, self.goal)
                    self.timer = 0
            elif self.state == "attack":
                new_goal = (player.x, player.y)
                if new_goal != self.goal:
                    self.goal = new_goal
                    self.move(grid, new_goal)
            self.timer += 1
            if self.timer >= 30:
                self.timer = 0
                if self.path_index < len(self.path):
                    self.x, self.y = self.path[self.path_index]
                    self.path_index += 1
        
        def draw(self, screen):
            center_x = (self.x * CELL_SIZE) + (CELL_SIZE // 2)
            center_y = (self.y * CELL_SIZE) + (CELL_SIZE // 2)
            screen.blit(npc_radius, (center_x - 23, center_y - 23))
            screen.blit(self.image, (center_x - 8, center_y - 8))

            if debug_Mode:
                if len(self.path) > 1:
                    points = [(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2) for x, y in self.path]
                    pygame.draw.lines(screen, (255, 0, 0), False, points, 3)

    def checkDamage():
        nonlocal pufferfish_health
        if (pufferfish_health > 0 and pufferfish.isHit(grid, fish) and not fish.hit_this_attack):
            pufferfish_health -= 1
            fish.hit_this_attack = True
        for t in turtles[:]:
            t.update(grid, fish)
            if t.isHit(grid, fish) and not fish.hit_this_attack:
                turtles.remove(t)
                fish.hit_this_attack = True

    def checkPlayerDamage(player):
        nonlocal endGame
        for t in turtles:
            if t.x == player.x and t.y == player.y:
                endGame = True
        if pufferfish.x == player.x and pufferfish.y == player.y and pufferfish_health > 0:
            endGame = True

    def checkTrap():
        nonlocal isTrapped, trapped, trap_timer
        if isTrapped:
            trapped = True
            trap_timer = 120
            isTrapped = False
        if trapped: 
            trap_timer -= 1
            if trap_timer <= 0:
                trapped = False

    pufferfish = NPC("puffer")
    turtles = []
    for i in range(5):
        turtle = NPC("turtle")
        turtles.append(turtle)

    #Game Run -----------------------------------------------------------------------------------------------------
    Algae_Score_Color_Text = (179, 255, 242)
    Coral_Score_Color_Text = (179, 222, 255)
    At_Goal_Color_Text = (255, 255, 255)
    AtGoal = "NO"

    def main_render():
        screen.fill((26, 63, 92))
        pygame.draw.line(screen, (255, 255, 255), (0, HEIGHT), (0, HEIGHT - 150), 2)
        pygame.draw.line(screen, (255, 255, 255), (WIDTH - 2, HEIGHT), (WIDTH - 2, HEIGHT - 150), 2)
        pygame.draw.line(screen, (255, 255, 255), (0, HEIGHT - 2), (WIDTH - 2, HEIGHT - 2), 2)
        pygame.draw.line(screen, (255, 255, 255), (WIDTH / 2, HEIGHT - 150), (WIDTH / 2, HEIGHT - 2), 2)

    def text_render():
        nonlocal Algae_Score_Color_Text, Coral_Score_Color_Text
        if ALGAE_COLLECTED >= 5:
            Algae_Score_Color_Text = (142, 255, 120)
        if CORAL_COLLECTED >= 10:
            Coral_Score_Color_Text = (142, 255, 120)
        if fish.x == GRID_COLS - 1 and fish.y == GRID_ROWS - 1:
            AtGoal = "YES"
            At_Goal_Color_Text = (142, 255, 120)
        else:
            AtGoal = "NO"
            At_Goal_Color_Text = (255, 255, 255)
                    
        screen.blit(font_default.render("> 'M' to toggle debug mode", True, (255, 255, 255)), (WIDTH / 2 + 10, HEIGHT - 140))
        screen.blit(font_default.render("> 'ARROW KEYS' to Move", True, (255, 255, 255)), (WIDTH / 2 + 10, HEIGHT - 120))
        screen.blit(font_default.render("> 'SPACE' to attack", True, (255, 255, 255)), (WIDTH / 2 + 10, HEIGHT - 100))

        screen.blit(font_default.render(f"Algae Collected: {ALGAE_COLLECTED} / 5", True, Algae_Score_Color_Text), (10, HEIGHT - 140))
        screen.blit(font_default.render(f"Coral Collected: {CORAL_COLLECTED} / 10", True, Coral_Score_Color_Text), (10, HEIGHT - 120))
        screen.blit(font_default.render(f"Is at Goal: [{AtGoal}]", True, At_Goal_Color_Text), (10, HEIGHT - 100))

        if debug_Mode:
            screen.blit(font_default.render(f"Boss NPC State: {pufferfish.state}", True, (255, 255, 255)), (WIDTH / 2 + 10, HEIGHT - 50))

    running = True
    menuPage = True
    endGame = False
    gameComplete = False
    trapped = False
    isTrapped = False

    while running:
        #keyboard input------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and menuPage:
                if event.key == pygame.K_SPACE:
                    menuPage = False
            if event.type == pygame.KEYDOWN and not (menuPage or endGame or gameComplete or trapped):
                if event.key == pygame.K_UP:
                    fish.moveCells(0, -1, grid)
                if event.key == pygame.K_DOWN:
                    fish.moveCells(0, 1, grid)
                if event.key == pygame.K_RIGHT:
                    fish.moveCells(1, 0, grid)
                if event.key == pygame.K_LEFT:
                    fish.moveCells(-1, 0, grid)
                if event.key == pygame.K_SPACE and (CORAL_COLLECTED > 1 or ALGAE_COLLECTED > 1):
                    fish.attack()
                if event.key == pygame.K_m:
                    if debug_Mode:
                        debug_Mode = False
                    else:
                        debug_Mode = True
        
        if not (menuPage or endGame or gameComplete):
            #Updates-----------------------------------------------------
            isCollected()
            fish.update()
            pufferfish.update(grid, fish)
            checkDamage()
            checkPlayerDamage(fish)
            checkTrap()

            if ALGAE_COLLECTED >= 5 and CORAL_COLLECTED >= 10 and (fish.x == GRID_COLS - 1 and fish.y == GRID_ROWS - 1):
                gameComplete = True
            
            #Rendering---------------------------------------------------
            main_render()
            text_render()
            for row in grid:
                for cell in row:
                    cell.draw(screen)
            for obj in corals:
                obj.draw()
            for obj in algaes:
                obj.draw()
            for obj in fuels:
                obj.draw()
            fish.draw()
            if pufferfish_health > 0:
                pufferfish.draw(screen)
            for t in turtles:
                t.draw(screen)
            if trapped:
                screen.blit(trap_image, ((WIDTH / 2) - 130, (HEIGHT / 2) - 45))
        
        if menuPage:
            screen.blit(menu, (0, 0))
        
        if endGame:
            screen.blit(endGame_image, (0, 0))

        if gameComplete:
            screen.blit(gameComplete_image, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()
asyncio.run(main())
