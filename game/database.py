"""Persistência de pontuações e ranking em SQLite."""
import sqlite3
from game.config import CAMINHO_BANCO


class ScoreDatabase:
    """Gerencia a tabela nomes_pontos no banco SQLite."""

    def __init__(self, caminho_banco: str = CAMINHO_BANCO) -> None:
        self.caminho_banco = caminho_banco
        self._garantir_tabela()

    def _garantir_tabela(self) -> None:
        with sqlite3.connect(self.caminho_banco) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS nomes_pontos (Score INTEGER, Name TEXT)"
            )
            conn.commit()

    def salvar_pontuacao(self, pontos: int, nome: str) -> None:
        with sqlite3.connect(self.caminho_banco) as conn:
            conn.execute(
                "INSERT INTO nomes_pontos (Score, Name) VALUES (?, ?)",
                (int(pontos), str(nome)),
            )
            conn.commit()

    def obter_top_10(self) -> list[tuple[int, int, str]]:
        """Retorna até 10 registros ordenados pelo menor tempo (Score crescente)."""
        with sqlite3.connect(self.caminho_banco) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT rowid, Score, Name FROM nomes_pontos ORDER BY Score ASC LIMIT 10"
            )
            return cursor.fetchall()
