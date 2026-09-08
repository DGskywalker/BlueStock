import importlib
p1 = importlib.import_module("pages.01_home")
render_home_page = p1.render_home_page
