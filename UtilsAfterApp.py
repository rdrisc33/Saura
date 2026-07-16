# SHOULD I PUT APP HERE? SUCH THAT APP IS ALWAYS BEFORE invoking qApp??? 
# from PySide6.QtWidgets import QApplication 
# import sys 
# app = QApplication(sys.argv) # I can access app instance elsewhere by 'from UtilsAfterApp import app'

# class UtilsAfterApp(): # import this AFTER you instantiate your app, so you can use QApp. 
#     file_grid_step = 1.27 # kicad symbols are designed on.05inche grid,  with metric mm measurements. .05inches = 1.27mm 
#     # scene_grid_step = 50 # A 50 pixel grid_step( preferable to use mm units over pixel units tho)
#     dpi = qApp.screens()[0].physicalDotsPerInch() 
#     print('GOT DPI:', dpi)
#     # snap wire vertices, symbol terminals, and symbols, to a ? unit grid_step 
#     scene_grid_step = ( ( dpi/25.4 ) * 4 ) # equals approx 17.8 on my laptop; a 17.8 pixel wide grid_step corresponds to 4mm    
#     kicad_symbol_scale_factor = 1/file_grid_step * scene_grid_step # scale_factor = 1/1.27 * 50 
#     board_grid_step = ( ( dpi/25.4 ) * 1 ) # The default grid for the board should be ? mm 
    