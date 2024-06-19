# version-0.2
import pygame
import random
import time
import threading
from copy import deepcopy
from collections import deque

simulating = False
#########################
def getboardscore(board) -> int:

    boardscore = 0
    board = deepcopy(board)
    
    # for j in range(3):
    #     for i in range(4):
    #         j1 = board[i][j]
    #         if not j1:j1 = 0
    #         j2 = board[i][j+1]
    #         if not j2:j2 = 0
    #         boardscore -= abs(j2-j1)
        
    for i in range(4):
        for j in range(4):
            boardscore += board[i][j]**2
            for x,y in [(-1,0),(1,0),(0,-1),(0,1)]:
                if (0<=i+x<4 and 0<=j+y<4):
                    Factor = board[i+x][j+y] if board[i+x][j+y] else board[i][j] >> 2
                else: Factor = board[i][j] >> 1
                boardscore += board[i][j]*Factor

    return boardscore

def generate_new(boardx):
    board_list=[]
    for i in range(4):
        for j in range(4):
            if boardx[i][j] == 0:
                newboard1 = [row[:] for row in boardx]
                newboard1[i][j] = 2
                newboard2 = [row[:] for row in boardx]
                newboard2[i][j] = 4
                board_list += [newboard1,newboard2]

    # board_list = [boardx[:i]+[(boardx[i][:j]+[2, 4])+(boardx[i][j+1:] if j<3 else [])] \
    #               +boardx[i+1:] for i in range(4) for j in range(4) if boardx[i][j]==0]
    return board_list

def in_simulation(func):
    def wrapper(*args,**kwargs):
        global simulating
        simulating = True
        res = func(*args,**kwargs)
        simulating = False
        return res
    return wrapper

class Boardtree():
    def __init__(self,currentboard,order='',branches=None) -> None:
        self.order = order
        self.currentboard = currentboard
        if branches: self.branches = branches
            
        else:self.branches = [[],[],[],[]]

    @staticmethod
    @in_simulation
    def board_next(board,movement):
        board_before = deepcopy(board)
        movement(board)
        if board != board_before:
            return generate_new(board)
        else:
            return None

    def addbranches(self,i,movement,direction):
        board_next_list = self.board_next(self.currentboard.copy(),movement)
        if board_next_list:
            for x in board_next_list:
                newboardtree = Boardtree(x,self.order + direction)
                self.branches[i].append(newboardtree)
        else: self.branches[i] = None

    def grow(self):
            self.addbranches(0,move_left,'l')
            self.addbranches(1,move_right,'r')
            self.addbranches(2,move_up,'u')
            self.addbranches(3,move_down,'d')

    @staticmethod
    def getmax(listwithNone):
        list_filtered = list(filter(lambda x: x is not None, listwithNone))
        if list_filtered != []: return max(list_filtered)
        else: return -100000

    @staticmethod
    def getmovescore(self):
        if self.branches==[[],[],[],[]]:
            return [getboardscore(self.currentboard)]*4
        else:
            score_list = [0,0,0,0]
            for i in range(4):
                if self.branches[i] is not None:
                    score_list_i = [self.getmax(self.getmovescore(x)) for x in self.branches[i]]
                    score_list[i] = sum(score_list_i)/len(score_list_i)
                else: score_list[i] = None
            return score_list
    

    def getbestmove(self):
        movescore = self.getmovescore(self)
        max_index = movescore.index(self.getmax(movescore))
        return [move_left,move_right,move_up,move_down][max_index]

def simulate(board,depth=2):
    boardtree1 = Boardtree(board)
    boardtrees = [boardtree1]

    def twoD_to_oneD(lst):
        return [elem for row in lst if row for elem in row]
    
    for _ in range(depth):
        for boardtree in boardtrees:
            boardtree.grow()
            boardtrees = twoD_to_oneD(boardtree.branches)

    boardtree1.getbestmove()(board)


# def simulate(board,depth=3):
#     boad_before = board.copy()
#     moves = [move_left, move_right, move_up, move_down]
#     move_scores = []

#     for move in moves:
#         board_copy = board[:]
#         move(board_copy)
#         if board_copy != boad_before:
#             score_list = [getboardscore(x) for x in generate_new(board_copy)]
#             score = sum(score_list) / len(score_list)
#         else:
#             score = -float('inf')
#         move_scores.append((score, move))

#     best_move = max(move_scores, key=lambda x: x[0])[1]
#     best_move(board)
####################
# 初始化Pygame
pygame.init()

# 设置窗口尺寸
WINDOW_SIZE = 410
STATUS_HEIGHT = 120

# 创建窗口
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE+STATUS_HEIGHT))
pygame.display.set_caption("2048 Game")

# 定义覆盖层
overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE+STATUS_HEIGHT)) # 覆盖层
overlay.set_alpha(128)  # 设置alpha值
overlay.fill((255, 255, 255))  # 用白色填充
overlayed = False

# 定义字体
NUM_FONT = pygame.font.SysFont(None, 50)
TEXT_FONT = pygame.font.SysFont("Arial", 30, True, True)
MiniTEXT_FONT = pygame.font.SysFont(None,25)
def varNUM_FONT(size):
    return pygame.font.SysFont(None, size)

# 定义方块尺寸和间隙
BLOCK_SIZE = 90
GAP_SIZE = 10

# 定义颜色常量
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)

# 定义游戏板块的初始状态
board = []
board_last = deque([])
max_retreat_step = 20
score = 0

# 获取某个方块的颜色
def get_block_color(number):
    if number == 0:
        return (200,200,200)
    elif number == 2:
        return WHITE
    elif number == 4:
        return (255, 255, 128)
    elif number == 8:
        return (255, 128, 0)
    elif number == 16:
        return (255, 0, 0)
    elif number == 32:
        return (255, 128, 128)
    elif number == 64:
        return (255, 0, 255)
    elif number == 128:
        return (128, 255, 128)
    elif number == 256:
        return (128, 128, 255)
    elif number == 512:
        return (128, 255, 255)
    elif number == 1024:
        return (255, 128, 192)
    elif number == 2048:
        return (255, 192, 128)
    elif number == 4096:
        return (128, 255, 192)
    elif number == 9192:
        return (128, 255, 192)

# 绘制分数
def draw_score():
    score_text = TEXT_FONT.render("Score: " + str(score), True, BLACK)
    score_rect = pygame.Rect(GAP_SIZE, WINDOW_SIZE, 180, 40)
    #score_rect.center = (GAP_SIZE + score_rect.width/2 , WINDOW_SIZE + STATUS_HEIGHT / 2)
    screen.fill((200, 200, 200), score_rect)
    screen.blit(score_text, score_rect)
    
    undo_text_lines = "Backspace to undo, \ncost:50".splitlines()
    for i, line in enumerate(undo_text_lines):
        line_text = MiniTEXT_FONT.render(line, True, BLACK)
        line_rect = line_text.get_rect()
        line_rect.left = GAP_SIZE
        line_rect.top = WINDOW_SIZE+STATUS_HEIGHT/2 + i * line_rect.height
        screen.fill(GRAY, line_rect)
        screen.blit(line_text, line_rect)
    pygame.display.update()

# 随机生成一个2或4
def generate_number():
    if random.randint(0, 1) == 0:
        return 2
    else:
        return 4

# 在随机位置生成一个数字
def generate_new_number():
    global board
    while True:
        x = random.randint(0, 3)
        y = random.randint(0, 3)
        if board[x][y] == 0:
            board[x][y] = generate_number()            
            draw_newblock(y,x,board[x][y])
            break

# 绘制新方块
def draw_newblock(y, x, num):
    Y = y* (BLOCK_SIZE + GAP_SIZE) + GAP_SIZE
    X = x* (BLOCK_SIZE + GAP_SIZE) + GAP_SIZE
    color = get_block_color(num)
    for i in range(0,51,2):
        pygame.draw.rect(screen, color, (Y+BLOCK_SIZE*(0.5-i/100), X+BLOCK_SIZE*(0.5-i/100), BLOCK_SIZE*i/50, BLOCK_SIZE*i/50))
        text = varNUM_FONT(i).render(str(num), True, BLACK)
        text_rect = text.get_rect()
        text_rect.center = (Y + BLOCK_SIZE / 2, X + BLOCK_SIZE / 2)
        screen.blit(text, text_rect)
        
        time.sleep(0.005)
        pygame.display.update()
    
# 绘制游戏板块
def draw_board():
    for i in range(4):
        for j in range(4):
            x = j * (BLOCK_SIZE + GAP_SIZE) + GAP_SIZE
            y = i * (BLOCK_SIZE + GAP_SIZE) + GAP_SIZE
            draw_block(x, y, board[i][j])
    pygame.display.update()

# 绘制方块
def draw_block(x, y, number):
    color = get_block_color(number)
    pygame.draw.rect(screen, color, (x, y, BLOCK_SIZE, BLOCK_SIZE))
    if number > 0:
        text = NUM_FONT.render(str(number), True, BLACK)
        text_rect = text.get_rect()
        text_rect.center = (x + BLOCK_SIZE / 2, y + BLOCK_SIZE / 2)
        screen.blit(text, text_rect)

# 绘制按钮

def draw_button_newgame(color):
    pygame.draw.rect(screen, GREEN, new_game_button_rect)
    new_game_button_text = TEXT_FONT.render("New Game", True, color)
    new_game_button_text_rect = new_game_button_text.get_rect(center=new_game_button_rect.center)
    screen.blit(new_game_button_text, new_game_button_text_rect)
    pygame.display.update()

def draw_button_auto():
    pygame.draw.rect(screen, (255,255,70), auto_button_rect)
    button_text = TEXT_FONT.render("Auto", True, BLACK)
    button_text_rect = button_text.get_rect(center=auto_button_rect.center)
    screen.blit(button_text, button_text_rect)
    pygame.display.update()

def draw_button(color_newgame):
    draw_button_newgame(color_newgame)
    draw_button_auto()

# 合并数字
def merge(row):
    global score
    score_o = score
    j = 0
    while j < len(row) - 1:
        if row[j] != 0 and row[j] == row[j+1]:
            row[j] *= 2
            if not simulating:
                score += row[j]
            row[j+1] = 0
            j += 2
        else: j += 1
    if score != score_o:
        draw_score()
        return True

# 翻转数组
def flip(array):
    return [list(reversed(row)) for row in array]

# 转置数组
def transpose(array):
    return [list(x) for x in zip(*array)]

# 处理向左移动
def move_left(board):
    for i in range(len(board)):
        def realign():
            board[i]=[board[i][j] for j in range(len(board[i])) if board[i][j] != 0] + [0] * board[i].count(0)
        realign()
        # while(merge(board[i])):
        #     realign()
        merge(board[i])
        realign()

# 处理向右移动
def move_right(board):
    board[:] = flip(board)
    move_left(board)
    board[:] = flip(board)

# 处理向上移动
def move_up(board):
    board[:] = transpose(board)
    move_left(board)
    board[:] = transpose(board)

# 处理向下移动
def move_down(board):
    board[:] = transpose(board)
    move_right(board)
    board[:] = transpose(board)

# 检查是否新增方块
def check_add_new(board_before):
    if board != board_before:
        draw_board()
        if len(board_last) == max_retreat_step:
            board_last.popleft()
        board_last.append(deepcopy(board_before))
        generate_new_number()

# 初始化游戏板块
def initialize_board():
    global board, board_last, score,overlayed
    board = [[0 for i in range(4)] for j in range(4)]
    board_last.clear()
    board_last.append(deepcopy(board))
    score = 0
    overlayed = False
    screen.fill(GRAY)
    draw_board()
    draw_score()
    draw_button(BLACK)
    pygame.display.update()
    gen1 = threading.Thread(target = generate_new_number)
    gen2 = threading.Thread(target = generate_new_number)
    gen1.start()
    gen2.start()
    gen1.join()
    gen2.join()

# 判断游戏是否结束
def is_game_over():
    for i in range(4):
        for j in range(4):
            if board[i][j] == 0:
                return False
            if j < 3 and board[i][j] == board[i][j+1]:
                return False
            if i < 3 and board[i][j] == board[i+1][j]:
                return False
    return True

# 绘制游戏结束界面
def draw_game_over():
    global overlay
    global overlayed

    if not overlayed:
        screen.blit(overlay, (0, 0))  # 将覆盖层绘制到屏幕上
        text = NUM_FONT.render("Game Over!", True, BLACK)
        text_rect = text.get_rect(center=(WINDOW_SIZE / 2, WINDOW_SIZE / 2))
        screen.blit(text, text_rect)
        overlayed = True

# 处理游戏逻辑
class autoprocess(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._running = True

    def run(self):
        global board_last
        while self._running:                  
            if not is_game_over():
                board_before = deepcopy(board)
                simulate(board)
                check_add_new(board_before)
            else: return

    def stop(self):
        self._running = False

def run_game():
    initialize_board()
    global board, board_last, score, overlayed

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                try:
                    autoprocess1.stop()
                    autoprocess1.join()
                except UnboundLocalError:
                    pass

                if event.key == pygame.K_BACKSPACE:
                    if board_last:
                        screen.fill(GRAY)
                        board = board_last.pop()
                        draw_board()
                        score -= 50
                        draw_score()
                        draw_button(BLACK)
                        overlayed = False
                        continue
                elif not is_game_over():                
                    board_before = deepcopy(board)
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        move_left(board)

                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        move_right(board)

                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        move_up(board)

                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        move_down(board)
    
                    check_add_new(board_before)
                        
                elif is_game_over():
                    draw_game_over()
                    draw_button(BLACK)
                    pygame.display.update()
                    continue

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                try:
                    autoprocess1.stop()
                    autoprocess1.join()
                except UnboundLocalError:
                    pass

                if new_game_button_rect.collidepoint(pygame.mouse.get_pos()):
                    draw_button(WHITE)

                    def detect_button_up():
                        while True:
                            for event in pygame.event.get():
                                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                                    draw_button(BLACK)
                                    if new_game_button_rect.collidepoint(pygame.mouse.get_pos()):
                                        initialize_board()
                                        overlayed = False
                                    return
                            pygame.time.wait(10)
                    detect_button_up()

                elif auto_button_rect.collidepoint(pygame.mouse.get_pos()):
                    
                    autoprocess1 = autoprocess()
                    autoprocess1.start()


        # 添加延时,不然太吃CPU
        pygame.time.wait(10)

# 运行游戏
if __name__ == "__main__":

    
    # 定义按钮
    new_game_button_rect = pygame.Rect(WINDOW_SIZE-200, WINDOW_SIZE+STATUS_HEIGHT/2, 190, 50)
    auto_button_rect = pygame.Rect(WINDOW_SIZE-200, WINDOW_SIZE, 190, 50)

    run_game()
