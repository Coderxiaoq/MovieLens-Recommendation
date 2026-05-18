#!/usr/bin/env python
"""
项目启动脚本
"""

import subprocess
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 启动 Streamlit 应用
def main():
    """启动应用"""
    app_path = PROJECT_ROOT / "src" / "app.py"
    
    if not app_path.exists():
        print(f"❌ 应用文件不存在: {app_path}")
        sys.exit(1)
    
    print(f"🚀 启动应用: {app_path}")
    print("💡 使用 Ctrl+C 停止应用\n")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(app_path)],
            cwd=str(PROJECT_ROOT),
            check=False
        )
    except KeyboardInterrupt:
        print("\n\n👋 应用已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
