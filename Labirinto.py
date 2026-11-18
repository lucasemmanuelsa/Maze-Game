"""Ponto de entrada principal do jogo Maze and Cannons."""
from game.engine import MazeGame


def main() -> None:
    jogo = MazeGame()
    jogo.executar()


if __name__ == "__main__":
    main()
