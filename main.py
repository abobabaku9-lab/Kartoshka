import os
import pygame
import sys

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Узнаем размер экрана устройства или ставим адаптивный режим под планшет/телефон
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
if WIDTH < 400: WIDTH = 800  # На всякий случай для эмуляторов
if HEIGHT < 400: HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("🥔 Картошкалоид DAW (Fixed Edition)")

# Цвета
BG_COLOR = (26, 26, 33)
GRID_LINE_COLOR = (45, 45, 60)
NOTE_COLOR = (64, 140, 217)
NOTE_BORDER_COLOR = (255, 255, 255)
TEXT_COLOR = (240, 240, 240)
PANEL_COLOR = (40, 40, 50)
BTN_COLOR = (70, 70, 90)
BTN_ACTIVE_COLOR = (200, 100, 50)

FONT = pygame.font.SysFont(None, 24)
BIG_FONT = pygame.font.SysFont(None, 32)

# --- ИСПРАВЛЕННЫЕ ПУТИ К БАНКАМ ---
# Ищем банки и в корне, и в папке banks/, чтобы ничего не потерялось
ROOT_BANKS_DIR = "banks"
os.makedirs(ROOT_BANKS_DIR, exist_ok=True)

# Создадим дефолтный банк прямо в banks/test_bank для порядка
default_bank_path = os.path.join(ROOT_BANKS_DIR, "test_bank")
os.makedirs(os.path.join(default_bank_path, "zapisi"), exist_ok=True)
os.makedirs(os.path.join(default_bank_path, "txts"), exist_ok=True)

if not os.path.exists(os.path.join(default_bank_path, "config.txt")):
    with open(os.path.join(default_bank_path, "config.txt"), "w", encoding="utf-8") as f:
        f.write("[0.000-1.000] a=a.wav\n[1.000-2.000] i=i.wav\n")
if not os.path.exists(os.path.join(default_bank_path, "txts", "passport.txt")):
    with open(os.path.join(default_bank_path, "txts", "passport.txt"), "w", encoding="utf-8") as f:
        f.write("Name: Картошка-чан\nAuthor: reywxyz\nIllustrator: AI")

available_banks = []
current_bank_path = default_bank_path
current_bank_name = "test_bank"
bank_data = {}  
bank_metadata = {"name": "Неизвестно", "author": "Неизвестно", "illustrator": "Неизвестно"}
current_lyric = "a"

def scan_banks():
    global available_banks
    available_banks = []
    # Сканируем папку banks/
    if os.path.exists(ROOT_BANKS_DIR):
        for entry in os.listdir(ROOT_BANKS_DIR):
            full_path = os.path.join(ROOT_BANKS_DIR, entry)
            if os.path.isdir(full_path):
                if os.path.exists(os.path.join(full_path, "config.txt")):
                    available_banks.append((entry, full_path))
    if not available_banks:
        available_banks = [("test_bank", default_bank_path)]

def load_bank(b_name, b_path):
    global bank_data, bank_metadata, current_bank_name, current_bank_path, current_lyric
    current_bank_name = b_name
    current_bank_path = b_path
    bank_data.clear()
    
    zapisi_dir = os.path.join(b_path, "zapisi")
    txts_dir = os.path.join(b_path, "txts")
    config_file = os.path.join(b_path, "config.txt")
    pass_file = os.path.join(txts_dir, "passport.txt")
    
    bank_metadata = {"name": b_name, "author": "Неизвестно", "illustrator": "Неизвестно"}
    if os.path.exists(pass_file):
        try:
            with open(pass_file, "r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line:
                        k, v = line.split(":", 1)
                        k, v = k.strip().lower(), v.strip()
                        if "name" in k: bank_metadata["name"] = v
                        elif "author" in k: bank_metadata["author"] = v
                        elif "illustrator" in k: bank_metadata["illustrator"] = v
        except Exception:
            pass

    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and "[" in line:
                        _, data_part = line.split("]")
                        lyric, filename = data_part.split("=")
                        lyric, filename = lyric.strip(), filename.strip()
                        full_path = os.path.join(zapisi_dir, filename)
                        bank_data[lyric] = {'file': full_path}
        except Exception:
            pass
            
    if bank_data:
        current_lyric = list(bank_data.keys())[0]

scan_banks()
load_bank(available_banks[0][0], available_banks[0][1])

def play_sound(lyric):
    if lyric in bank_data:
        fpath = bank_data[lyric]['file']
        if os.path.exists(fpath):
            try:
                sound = pygame.mixer.Sound(fpath)
                sound.play()
            except Exception as e:
                print(f"Ошибка звука: {e}")

notes = []
active_screen = 'menu'

# Размеры сетки пиано-ролла
CELL_W = 60
CELL_H = 35
TOP_PANEL_H = 70

clock = pygame.time.Clock()

while True:
    # Обновляем ширину/высоту если окно/планшет повернулся
    WIDTH, HEIGHT = screen.get_size()
    screen.fill(BG_COLOR)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            
            if active_screen == 'menu':
                if WIDTH // 2 - 150 <= mx <= WIDTH // 2 + 150:
                    if HEIGHT // 2 - 80 <= my <= HEIGHT // 2 - 35:
                        active_screen = 'studio'
                    elif HEIGHT // 2 - 20 <= my <= HEIGHT // 2 + 25:
                        active_screen = 'bank_selector'
                    elif HEIGHT // 2 + 40 <= my <= HEIGHT // 2 + 85:
                        active_screen = 'passport'
                    elif HEIGHT // 2 + 100 <= my <= HEIGHT // 2 + 145:
                        pygame.quit()
                        sys.exit()
                        
            elif active_screen == 'bank_selector':
                y_offset = 120
                for b_name, b_path in available_banks:
                    if 50 <= mx <= WIDTH - 50 and y_offset <= my <= y_offset + 50:
                        load_bank(b_name, b_path)
                        active_screen = 'studio'
                    y_offset += 60
                if 50 <= mx <= 200 and HEIGHT - 80 <= my <= HEIGHT - 30:
                    active_screen = 'menu'
                    
            elif active_screen == 'passport':
                if 50 <= mx <= 200 and HEIGHT - 80 <= my <= HEIGHT - 30:
                    active_screen = 'menu'
                    
            elif active_screen == 'studio':
                if my <= TOP_PANEL_H:
                    if 10 <= mx <= 80:  # Меню
                        active_screen = 'menu'
                    elif 90 <= mx <= 160:  # Play
                        for note in sorted(notes, key=lambda n: n['x']):
                            play_sound(note['lyric'])
                    elif 170 <= mx <= 290:  # Сменить банк
                        scan_banks()
                        active_screen = 'bank_selector'
                    else:
                        # Клики по слогам
                        btn_x = 300
                        for lyric in bank_data.keys():
                            if btn_x <= mx <= btn_x + 55:
                                current_lyric = lyric
                            btn_x += 65
                
                elif my > TOP_PANEL_H:
                    # Ставим/удаляем ноту ровно по сетке на весь экран
                    grid_x = (mx // CELL_W) * CELL_W
                    grid_y = ((my - TOP_PANEL_H) // CELL_H) * CELL_H
                    
                    existing_note = None
                    for note in notes:
                        if note['x'] == grid_x and note['y'] == grid_y:
                            existing_note = note
                            break
                    
                    if existing_note:
                        notes.remove(existing_note)
                    else:
                        new_note = {'x': grid_x, 'y': grid_y, 'lyric': current_lyric, 'width': CELL_W}
                        notes.append(new_note)
                        play_sound(current_lyric)

    # --- ОТРИСОВКА ---
    if active_screen == 'menu':
        title_surf = BIG_FONT.render("🥔 КАРТОШКАЛОИД DAW", True, TEXT_COLOR)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 2 - 150))
        
        btns = [
            ("🎹 Открыть Студию", HEIGHT // 2 - 80),
            ("📁 Выбрать Банк", HEIGHT // 2 - 20),
            ("📖 Паспорт Банка", HEIGHT // 2 + 40),
            ("❌ Выход", HEIGHT // 2 + 100)
        ]
        for text, y_pos in btns:
            color = (120, 40, 40) if "Выход" in text else BTN_COLOR
            pygame.draw.rect(screen, color, (WIDTH // 2 - 150, y_pos, 300, 45), border_radius=8)
            t = FONT.render(text, True, TEXT_COLOR)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, y_pos + 12))

    elif active_screen == 'bank_selector':
        title_surf = BIG_FONT.render("📁 Выбор голосового банка (в папке banks/)", True, TEXT_COLOR)
        screen.blit(title_surf, (50, 40))
        
        y_offset = 100
        for b_name, b_path in available_banks:
            bg_col = BTN_ACTIVE_COLOR if b_path == current_bank_path else BTN_COLOR
            pygame.draw.rect(screen, bg_col, (50, y_offset, WIDTH - 100, 50), border_radius=8)
            t = FONT.render(f"🎤 {b_name} ({b_path})", True, TEXT_COLOR)
            screen.blit(t, (70, y_offset + 15))
            y_offset += 65
            
        pygame.draw.rect(screen, BTN_COLOR, (50, HEIGHT - 80, 150, 40), border_radius=8)
        screen.blit(FONT.render("◀ Назад", True, TEXT_COLOR), (50 + 75 - FONT.render("◀ Назад", True, TEXT_COLOR).get_width()//2, HEIGHT - 70))

    elif active_screen == 'passport':
        title_surf = BIG_FONT.render(f"📄 Паспорт: {bank_metadata['name']}", True, TEXT_COLOR)
        screen.blit(title_surf, (50, 40))
        
        info_lines = [
            f"Имя банка: {bank_metadata['name']}",
            f"Автор: {bank_metadata['author']}",
            f"Иллюстратор: {bank_metadata['illustrator']}",
            f"Текущая папка: {current_bank_path}",
            f"Доступно слогов: {len(bank_data)}"
        ]
        y_offset = 100
        for line in info_lines:
            screen.blit(FONT.render(line, True, TEXT_COLOR), (50, y_offset))
            y_offset += 40
            
        pygame.draw.rect(screen, BTN_COLOR, (50, HEIGHT - 80, 150, 40), border_radius=8)
        screen.blit(FONT.render("◀ Назад", True, TEXT_COLOR), (50 + 75 - FONT.render("◀ Назад", True, TEXT_COLOR).get_width()//2, HEIGHT - 70))

    elif active_screen == 'studio':
        # Верхняя панель
        pygame.draw.rect(screen, PANEL_COLOR, (0, 0, WIDTH, TOP_PANEL_H))
        
        # Меню
        pygame.draw.rect(screen, BTN_COLOR, (10, 15, 75, 40), border_radius=5)
        screen.blit(FONT.render("Меню", True, TEXT_COLOR), (47 - FONT.render("Меню", True, TEXT_COLOR).get_width()//2, 25))
        
        # Play
        pygame.draw.rect(screen, (40, 140, 70), (95, 15, 75, 40), border_radius=5)
        screen.blit(FONT.render("▶ Play", True, TEXT_COLOR), (132 - FONT.render("▶ Play", True, TEXT_COLOR).get_width()//2, 25))

jl = f"📁 {current_bank_name}"
        # Кнопка банка
        pygame.draw.rect(screen, (150, 90, 40), (180, 15, 110, 40), border_radius=5)
        screen.blit(FONT.render(jl[:10], True, TEXT_COLOR), (235 - FONT.render(jl[:10], True, TEXT_COLOR).get_width()//2, 25))
        
        # Слоги
        btn_x = 300
        for lyric in bank_data.keys():
            color = BTN_ACTIVE_COLOR if lyric == current_lyric else BTN_COLOR
            pygame.draw.rect(screen, color, (btn_x, 15, 55, 40), border_radius=5)
            screen.blit(FONT.render(lyric, True, TEXT_COLOR), (btn_x + 27 - FONT.render(lyric, True, TEXT_COLOR).get_width()//2, 25))
            btn_x += 65

        pygame.draw.line(screen, (80, 80, 100), (0, TOP_PANEL_H), (WIDTH, TOP_PANEL_H), 2)
        
        # Сетка пиано-ролла на весь экран
        for x in range(0, WIDTH, CELL_W):
            pygame.draw.line(screen, GRID_LINE_COLOR, (x, TOP_PANEL_H), (x, HEIGHT), 1)
        for y in range(TOP_PANEL_H, HEIGHT, CELL_H):
            pygame.draw.line(screen, GRID_LINE_COLOR, (0, y), (WIDTH, y), 1)
            
        # Ноты
        for note in notes:
            rx = note['x']
            ry = note['y'] + TOP_PANEL_H
            if rx < WIDTH and ry < HEIGHT:
                pygame.draw.rect(screen, NOTE_COLOR, (rx, ry, note['width'], CELL_H - 3), border_radius=4)
                pygame.draw.rect(screen, NOTE_BORDER_COLOR, (rx, ry, note['width'], CELL_H - 3), 1, border_radius=4)
                screen.blit(FONT.render(note['lyric'], True, TEXT_COLOR), (rx + 6, ry + 6))

    pygame.display.flip()
    clock.tick(60)