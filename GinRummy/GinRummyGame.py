import logging
from typing import List

import numpy as np
from tqdm import tqdm

from Game import Game
import socket
log = logging.getLogger(__name__)

class GinRummyGame(Game):
    def __init__(self, host='127.0.0.1', port=12345):
        super().__init__()
        self.action_size = None
        self.board_size = None
        self.host = host
        self.port = port

    def send_message(self, command, state = None, player = None, action = None):
        payload = [command]
        if state is not None:
            payload = payload + state
        if player is not None:
            if player == -1:
                player = 1
            else:
                player = 0
            payload = payload + [player]
        if action is not None:
            payload = payload + [action]

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        message = bytearray(payload)
        try:
            client_socket.connect((self.host, self.port))
        #    log.info(f"\nServer send: {payload}")
            client_socket.sendall(message)
            response = list(client_socket.recv(57))
        #    log.info(f"\nServer response: {response}")
            if len(response) < 56:
                return [], list(response)
            state = np.array(response[:56]).reshape(self.getBoardSize())
            if len(response) == 57:
                player = response[56]
                if player is 1:
                    player = -1
                else:
                    player = 1
            return state, player
        except ConnectionError as e:
            tqdm.write(f"Connection error: {e}")
            quit()
        finally:
            # Close the socket
            client_socket.close()
        #    print("Disconnected from server.")

    def getInitBoard(self):
        state, player = self.send_message(0)
        return state

    def getBoardSize(self):
        if self.board_size is None:
            state, add = self.send_message(1)
            self.board_size = (add[0],add[1])
        return self.board_size

    def getActionSize(self):
        if self.action_size is None:
            state, add = self.send_message(2)
            self.action_size = add[0]
        return self.action_size

    def getNextState(self, board, player, action):
        state, player = self.send_message(3, board.flatten().tolist(), player, action)
        return state, player

    def getValidMoves(self, board, player):
        state, player = self.send_message(4, board.flatten().tolist(), player)
        return state.flatten()

    def getGameEnded(self, board, player):
        state, player = self.send_message(5, board.flatten().tolist(), player)
        state = player[0]
        if state==3:
            state = -0.01
        elif state==2:
            state = -1
        return state

    def getCanonicalForm(self, board, player):
        state, player = self.send_message(6, board.flatten().tolist(), player)
        return state

    def getSymmetries(self, board, pi):
        return [(board, pi)]

    def stringRepresentation(self, board):
        return ' '.join(map(str, board.flatten().tolist()))