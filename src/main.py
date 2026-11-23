import time

import extract
import load
import transform


def run():
    inicio = time.perf_counter()

    extract.run()
    transform.run()
    load.run()

    duracao = time.perf_counter() - inicio
    print(f"[main] Pipeline concluído em {duracao:.1f}s")


if __name__ == "__main__":
    run()