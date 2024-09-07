from cx_Freeze import setup, Executable


# 设置你的应用程序信息
setup(
    name="YourAppName",
    version="0.1",
    description="Your application description",
    executables=[Executable("main_old.py")]
)