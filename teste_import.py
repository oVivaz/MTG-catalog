# teste_import.py
print("Testando importações...")

try:
    import numpy as np
    print("✅ NumPy OK")
except Exception as e:
    print(f"❌ NumPy erro: {e}")

try:
    import pandas as pd
    print("✅ Pandas OK") 
except Exception as e:
    print(f"❌ Pandas erro: {e}")

input("Pressione Enter...")