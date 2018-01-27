import numpy as np
from simulator.enums import Field


def data_to_state(data, snake_direction):

    width = data['width']
    height = data['height']

    state = np.zeros([width + 3, height + 2], dtype=int)

    for x in range(0, width + 1):
        for y in range(0, height + 1):
            if x == 0 or y == 0 or x == width or y == height:
                state[x, y] = Field.body

    for snake in data['snakes']:
        for idx, [x, y] in enumerate(snake['coords']):
            if snake['id'] == data['you']:
                if idx == 0:
                    if snake_direction == 'up':
                        state[x][y] = Field.own_head_up
                    elif snake_direction == 'right':
                        state[x][y] = Field.own_head_right
                    elif snake_direction == 'down':
                        state[x][y] = Field.own_head_down
                    else:
                        state[x][y] = Field.own_head_left
                else:
                    state[x][y] = Field.own_tail if idx == len(snake['coords']) - 1 else Field.own_body
            else:
                state[x][y] = Field.head if idx == 0 else Field.tail if idx == len(
                    snake['coords']) - 1 else Field.body
            if snake['id'] == data['you']:
                state[width + 2][0] = snake['health_points']
    for [x, y] in data['food']:
        state[x][y] = Field.fruit

    return state