#!/usr/bin/env python3

"""
Script para executar a aplicação Instagram URL Converter localmente
"""

from main import app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000) 