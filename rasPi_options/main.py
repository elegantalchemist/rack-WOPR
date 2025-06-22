from machine import Pin, SPI
import max7219
import random
import time

DELAYS = {
  'slow': [500, 1000, 1500, 2000],
  'fast': [20, 50, 100, 200]
}

FAST_CHANCE = 0.05
FAST_RUN_TIME = 5000
RELAX_RUN_TIME = 5000

spi = SPI(0,sck=Pin(2),mosi=Pin(3))
cs = Pin(5, Pin.OUT)
display = max7219.Matrix8x8(spi, cs, 12)
display.brightness(1)

class WOPRController:
  SECTIONS = {
    'shifter':   { 'x':  0, 'y': 0, 'w':  8, 'h': 8 },
    'program-a': { 'x': 10, 'y': 0, 'w': 16, 'h': 4 },
    'a-counter': { 'x': 10, 'y': 6, 'w': 16, 'h': 2 },
    'life':      { 'x': 28, 'y': 0, 'w': 32, 'h': 8 },
    'program-b': { 'x': 62, 'y': 0, 'w': 16, 'h': 4 },
    'b-counter': { 'x': 62, 'y': 6, 'w': 16, 'h': 2 },
    'random':    { 'x': 80, 'y': 0, 'w': 16, 'h': 8 },
  }

  SEEDS = {
    'shifter':   [ 0xEC, 0x62, 0x38, 0x51, 0x36, 0x66, 0x59, 0x84 ],
    'program-a': [ 0x7018, 0x1C61, 0x0C0C, 0x3039 ],
    'program-b': [ 0x42AB, 0x0070, 0x06E2, 0x6064 ],
  }

  def __init__(self, display):
    self.section_ticks = [
      self.tick_section_shifter,
      self.tick_section_program_a,
      self.tick_section_a_counter,
      self.tick_life,
      self.tick_section_program_b,
      self.tick_section_b_counter,
      self.tick_section_random,
    ]

    self.display = display
    self.random_mode_fast = False
    self.shifter_next_update = 0
    self.section_shifter_init = False
    self.program_a_next_update = 0
    self.program_a_upper_override_expiry = 0
    self.program_a_lower_override_expiry = 0
    self.section_program_a_init = False
    self.a_counter_next_update = 0
    self.life_next_update = 0
    self.program_b_next_update = 0
    self.program_b_override_expiry = 0
    self.b_counter_next_update = 0
    self.b_counter_next_reset = 0
    self.b_counter_value = 0
    self.section_program_b_init = False
    self.random_mode_next_update = 0
    self.random_next_update = 0


  def init_section(self, section, seed):
    for y in range(section['h']):
      for x in range(section['w']):
        self.display.pixel(
          section['x'] + x,
          section['y'] + y,
          (seed[y] >> x) & 1
        )

  def tick_section_shifter(self):
    if time.ticks_diff(time.ticks_ms(), self.shifter_next_update) < 0:
      return False
    
    self.shifter_next_update = time.ticks_add(time.ticks_ms(), 700)

    if not self.section_shifter_init:
      self.init_section(self.SECTIONS['shifter'], self.SEEDS['shifter'])
      self.section_shifter_init = True
    
    self.display.shift_region(
      self.SECTIONS['shifter']['x'],
      self.SECTIONS['shifter']['y'],
      self.SECTIONS['shifter']['w'],
      self.SECTIONS['shifter']['h'],
      1,
      True
    )

    return True
  
  def tick_section_program_a(self):
    if time.ticks_diff(time.ticks_ms(), self.program_a_next_update) < 0:
      return False

    self.program_a_next_update = time.ticks_add(time.ticks_ms(), 100)

    if not self.section_program_a_init:
      self.init_section(self.SECTIONS['program-a'], self.SEEDS['program-a'])
      self.section_program_a_init = True

    now = time.ticks_ms()

    section = self.SECTIONS['program-a']
    x0 = section['x']
    y0 = section['y']
    w = section['w']
    h = section['h']
    half_h = h // 2

    normal_shift = -1  # default shift direction and speed

    # Upper half override check:
    if time.ticks_diff(self.program_a_upper_override_expiry, now) > 0:
      upper_shift = self.program_a_upper_override_value
    else:
      # Normally use normal_shift, but with a 10% chance override:
      if random.random() < 0.1:
        if random.random() < 0.5:
          shift_val = 0  # pause
        else:
          shift_val = random.randint(1, 3)  # reverse direction with variable speed
        upper_shift = shift_val

        # Hold the override for a random duration between 300 and 1000 ms
        override_duration = random.randint(300, 1000)
        self.program_a_upper_override_expiry = time.ticks_add(now, override_duration)
        self.program_a_upper_override_value = shift_val
      else:
        upper_shift = normal_shift
        self.program_a_upper_override_expiry = now  # disable override

    # Lower half override check:
    if time.ticks_diff(self.program_a_lower_override_expiry, now) > 0:
      lower_shift = self.program_a_lower_override_value
    else:
      # Normally use normal_shift, but with a 10% chance override:
      if random.random() < 0.1:
        if random.random() < 0.5:
          shift_val = 0  # pause
        else:
          shift_val = random.randint(1, 3)  # reverse direction with variable speed
        lower_shift = shift_val

        # Hold the override for a random duration between 300 and 1000 ms
        override_duration = random.randint(300, 1000)
        self.program_a_lower_override_expiry = time.ticks_add(now, override_duration)
        self.program_a_lower_override_value = shift_val
      else:
        lower_shift = normal_shift
        self.program_a_lower_override_expiry = now  # disable override

    self.display.shift_region(x0, y0, w, half_h, upper_shift, True)
    self.display.shift_region(x0, y0 + half_h, w, h - half_h, lower_shift, True)

    return True

  def tick_section_a_counter(self):
    if time.ticks_diff(time.ticks_ms(), self.a_counter_next_update) < 0:
      return False
    
    self.a_counter_next_update = time.ticks_add(time.ticks_ms(), 100)

    # this function represents the counter value of time.ticks_ms and refreshes every 100ms
    # the counter is displayed in the 'a-counter' section
    counter = time.ticks_ms()
    for y in range(self.SECTIONS['a-counter']['h']):
      for x in range(self.SECTIONS['a-counter']['w']):
        self.display.pixel(
          self.SECTIONS['a-counter']['x'] + self.SECTIONS['a-counter']['w'] - x - 1,
          self.SECTIONS['a-counter']['y'] + y,
          (counter >> (y * 4 + x)) & 1
        )
    
    return True

  def init_life_board(self):
    w = self.SECTIONS['life']['w']
    h = self.SECTIONS['life']['h']
    self.life_board = [[random.randint(0, 1) for _ in range(w)] for _ in range(h)]
    for y in range(h):
      for x in range(w):
        self.display.pixel(
          self.SECTIONS['life']['x'] + x,
          self.SECTIONS['life']['y'] + y,
          self.life_board[y][x]
        )
    # Set/reset the 60-second timer for this board
    self.life_reset_time = time.ticks_ms()
    # Clear previous history
    self.prev_life_board = None
    self.prev2_life_board = None

  def tick_life(self):
    if time.ticks_diff(time.ticks_ms(), self.life_next_update) < 0:
      return False

    self.life_next_update = time.ticks_add(time.ticks_ms(), 50)
    w = self.SECTIONS['life']['w']
    h = self.SECTIONS['life']['h']

    # Initialize the Life board if it doesn't exist
    if not hasattr(self, 'life_board'):
      self.init_life_board()
      return True

    new_board = [[0 for _ in range(w)] for _ in range(h)]
    for y in range(h):
      for x in range(w):
        live_neighbors = 0
        # Check neighbors with wrap-around
        for dy in [-1, 0, 1]:
          for dx in [-1, 0, 1]:
            if dy == 0 and dx == 0:
              continue
            ny = (y + dy) % h
            nx = (x + dx) % w
            live_neighbors += self.life_board[ny][nx]
        # Apply Conway's rules
        if self.life_board[y][x] == 1:
          if live_neighbors < 2 or live_neighbors > 3:
            new_board[y][x] = 0
          else:
            new_board[y][x] = 1
        else:
          if live_neighbors == 3:
            new_board[y][x] = 1
          else:
            new_board[y][x] = 0

    # Detect stale board if:
    # - new_board is the same as the most recent previous board, OR
    # - new_board is the same as the board two cycles ago, OR
    # - all cells are dead, OR
    # - the board has been alive for 60 seconds.
    if ((self.prev_life_board is not None and new_board == self.prev_life_board) or
        (self.prev2_life_board is not None and new_board == self.prev2_life_board) or
        not any(cell for row in new_board for cell in row) or
        time.ticks_diff(time.ticks_ms(), self.life_reset_time) >= 60000):
      self.init_life_board()
      return True

    # Update the display with the new board state
    for y in range(h):
      for x in range(w):
        self.display.pixel(
          self.SECTIONS['life']['x'] + x,
          self.SECTIONS['life']['y'] + y,
          new_board[y][x]
        )

    # Update the history: shift previous boards back by one cycle.
    self.prev2_life_board = [row[:] for row in self.prev_life_board] if self.prev_life_board is not None else None
    self.prev_life_board = [row[:] for row in self.life_board]
    self.life_board = new_board

    return True

  def tick_section_program_b(self):
    if time.ticks_diff(time.ticks_ms(), self.program_b_next_update) < 0:
      return False

    self.program_b_next_update = time.ticks_add(time.ticks_ms(), 150)

    if not self.section_program_b_init:
      self.init_section(self.SECTIONS['program-b'], self.SEEDS['program-b'])
      self.section_program_b_init = True

    now = time.ticks_ms()
    normal_shift = 2

    # Check for a current override: if the override expiry is still in the future,
    # use the override value
    if time.ticks_diff(self.program_b_override_expiry, now) > 0:
      shift_val = self.program_b_override_value
    else:
      # With a 10% chance, choose an override value and hold it for a random duration
      # before reverting to normal
      if random.random() < 0.1:
        # Pick a random shift from -3 to 3 (excluding 0 to avoid a pause)
        shift_val = random.choice([-3, -2, -1, 1, 2, 3])
        hold_duration = random.randint(1000, 3000)  # hold in ms
        self.program_b_override_expiry = time.ticks_add(now, hold_duration)
        self.program_b_override_value = shift_val
      else:
        shift_val = normal_shift
        # Reset override expiry so future ticks can decide on a new override
        self.program_b_override_expiry = now

    self.display.shift_region(
      self.SECTIONS['program-b']['x'],
      self.SECTIONS['program-b']['y'],
      self.SECTIONS['program-b']['w'],
      self.SECTIONS['program-b']['h'],
      shift_val,
      True
    )

    return True

  def tick_section_b_counter(self):
    if time.ticks_diff(time.ticks_ms(), self.b_counter_next_update) < 0:
      return False

    self.b_counter_next_update = time.ticks_add(time.ticks_ms(), 200)

    if time.ticks_diff(time.ticks_ms(), self.b_counter_next_reset) >= 0:
      self.b_counter_value = random.getrandbits(32)
      duration = random.randint(20, 60) * 1000
      self.b_counter_next_reset = time.ticks_add(time.ticks_ms(), duration)

    counter = self.b_counter_value
    self.b_counter_value -= 1

    for y in range(self.SECTIONS['b-counter']['h']):
      for x in range(self.SECTIONS['b-counter']['w']):
        self.display.pixel(
          self.SECTIONS['b-counter']['x'] + self.SECTIONS['b-counter']['w'] - x - 1,
          self.SECTIONS['b-counter']['y'] + y,
          (counter >> (y * 4 + x)) & 1
        )

    return True

  def tick_section_random(self):
    if time.ticks_diff(time.ticks_ms(), self.random_next_update) < 0:
      return False

    delay = random.choice(DELAYS['fast' if self.random_mode_fast else 'slow'])
    self.random_next_update = time.ticks_add(time.ticks_ms(), delay)

    for y in range(self.SECTIONS['random']['h']):
      for x in range(self.SECTIONS['random']['w']):
        if random.randint(0, 1) == 0:
          self.display.pixel(
            self.SECTIONS['random']['x'] + x,
            self.SECTIONS['random']['y'] + y,
            random.randint(0, 1)
          )

    return True

  def update_random_mode(self):
    if time.ticks_diff(time.ticks_ms(), controller.random_mode_next_update) >= 0:
      if self.random_mode_fast:
        self.random_mode_next_update = time.ticks_add(time.ticks_ms(), RELAX_RUN_TIME)
        self.random_mode_fast = False
      else:
        self.random_mode_next_update = time.ticks_add(time.ticks_ms(), FAST_RUN_TIME)
        if random.random() <= FAST_CHANCE:
          self.random_mode_fast = True

  def run(self):
    while True:
      should_update_display = False

      for tick in self.section_ticks:
        should_update_display |= tick()

      if should_update_display:
        self.display.show()

controller = WOPRController(display)
controller.run()
