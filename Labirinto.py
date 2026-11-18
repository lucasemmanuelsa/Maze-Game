"""Ponto de entrada principal do jogo Maze and Cannons (1 a 3 jogadores locais)."""
import argparse
import os
from game.engine import MazeGame


def main() -> None:
    parser = argparse.ArgumentParser(description="Maze and Cannons")
    parser.add_argument(
        "--nivel",
        type=int,
        default=int(os.environ.get("MAZE_START_LEVEL", "1")),
        help="Nível inicial para iniciar o jogo (padrão: 1)",
    )
    parser.add_argument(
        "--jogadores",
        type=int,
        choices=(1, 2, 3),
        default=int(os.environ.get("MAZE_PLAYERS", "1")),
        help="Quantidade de jogadores locais: 1, 2 ou 3 (padrão: 1)",
    )
    parser.add_argument(
        "--direto",
        action="store_true",
        default=os.environ.get("MAZE_SKIP_MENU", "0") == "1",
        help="Pula intro e menu para testar uma fase rapidamente",
    )
    args, _ = parser.parse_known_args()

    jogo = MazeGame()
    jogo.executar(
        nivel_inicial=args.nivel,
        pular_menu=args.direto,
        num_jogadores=args.jogadores,
    )


if __name__ == "__main__":
    main()
