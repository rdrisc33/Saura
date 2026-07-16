from utils import * 


def main():

    # app = QAppli cation(sys.argv) # SECOND, I instantiate app (Moved to Utils )|

    from MainWindow import MainWindow # THEN I import everything else, only because Screen DPI info is needed in like 2 lines, but I have to already have instantiated app in order to access screen information. Q: Good practice? bad practice? 

    window = MainWindow()
    # window.resize(qApp.primaryScreen().availableGeometry().size()*.3) # My MW's table is rendering off-screen. This line serves to make MW narrow...
    # window.setMaximumHeight(qApp.primaryScreen().availableGeometry().height()) DNW either
    # window.setFixedHeight(300) # Works; prevents resizing



    # window.setMaximumHeight(300) # ignored( layouts will override this) (but DOES prevent snapping)

    # print(qApp.primaryScreen().availableGeometry().size()) # 1536, 960

    # window.resize(400,400) 
    # print('SIZE:', window.size()) # (400, 400)# NOT SEEING 400x400 tho
    # print('GEOM:', window.geometry()) # (400,400)
    # print('MIN:', window.minimumHeight())
    # print('MAX:', window.maximumHeight())
    
    # print()
    # print('SIZE:', window.size())# (640, 480) # NOT SEEING 640x680 
    # print('GEOM:', window.geometry())
    # window.setFixedSize(640, 640) # NOW I see 640x480, wth? 

    
    window.show()   


#  create_part is not refreshing |table
    sys.exit(app.exec())
        
if __name__ == "__main__":
    main()

# [parameters: ('battery products,batteries rechargeable (secondary)',
#               {'battery cell size': 'AAA', '|battery chemistry': 'Nickel Metal Hydride', 'capacity': '900mAh', 'size/dimension': '0.41" Dia x 1.75" H (10.5mm x 44.5mm)', 'termination style': 'Button Top (Extending)', 'voltage_rated': '1.2 V'}


