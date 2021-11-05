from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import time
from ToothPaint_CV import*

CV = Paint_CV()
class Paint(QMainWindow):
    def __init__(self):
        self.new = True
        self.selection = False
        self.Move = False
        self.toolSelected = 0
        self.complete_selection = False
        self.init_coords = []
        self.color = (0,0,0)
        self.color_bg = (255,255,255)
        self.thickness = 1
        self.point = False
        self.zoom = [1,1]
        self.Aspc_ratio = True
        self.resize_value=[100,100,0,0]
        self.grid = 0
        self.font = [0, 1.0]
        super(Paint,self).__init__()
        self.resize(1100, 770)
        self.setWindowIcon(QIcon("TP_assets/icon.png"))
        self.setWindowTitle("TOOTH PAINT by Low Jun Hong BS18110173")
        self.SplashScreen()
        self.initUI()

    def closeEvent(self, event):
        event.ignore()
        self.QuitDialog()

    def initUI(self):
        self.background = QLabel(self)
        self.background.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.background.setScaledContents(True)
        self.background.setAlignment(Qt.AlignTop)
        tracker = MouseTracker(self.background)
        tracker.positionChanged.connect(self.DetectPOS)
        self.zoom_slider = self.SliderWidget(Qt.Horizontal, 100, 1, 500, 150, lambda :self.zoomTool(1))
        self.zoom_percentage = self.Label_TextOnly("\t100%", ('Calibri', 10))
        plus_btn = self.PushBtnIcon("TP_assets/plus.png", lambda :self.zoomTool(2))
        minus_btn = self.PushBtnIcon("TP_assets/minus.png", lambda :self.zoomTool(3))
        self.pixel_dim = self.Label_TextOnly("Dimension :      -      ", ('Calibri', 10))
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.background)
        self.setCentralWidget(self.scrollArea)
        self.statusBar()
        self.statusBar().setStyleSheet('background-color: #e3e3e3;QStatusBar::item {border: none;}')
        self.statusBar().addPermanentWidget(VLine())
        self.statusBar().addPermanentWidget(self.pixel_dim)
        self.statusBar().addPermanentWidget(VLine())
        self.statusBar().addPermanentWidget(self.zoom_percentage)
        self.statusBar().addPermanentWidget(minus_btn)
        self.statusBar().addPermanentWidget(self.zoom_slider)
        self.statusBar().addPermanentWidget(plus_btn)
        tracker3 = MouseTracker(self.statusBar())
        tracker3.positionChanged.connect(self.DetectPOS2)
        self.Menubars()
        self.Toolbars()
        self.TextEdit = QLineEdit(self)
        self.TextEdit.setText("Please Enter Here")
        self.TextEdit.textChanged.connect(self.UpdateText)
        self.TextEdit.hide()

    def DetectPOS(self, pos):
        if 1<=self.toolSelected<=7:
            QApplication.setOverrideCursor(Qt.CrossCursor)
        elif self.toolSelected==8 and not self.point:
            QApplication.setOverrideCursor(Qt.IBeamCursor)
        elif self.toolSelected==9:
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)
        elif self.toolSelected==10:
            QApplication.setOverrideCursor(Qt.PointingHandCursor)
        self.cursor_OUT = False
        self.statusBar().showMessage(str(pos.x()) + ", " + str(pos.y()) + "px")
        if self.toolSelected==1 and self.complete_selection:
            mouse_x, mouse_y = int(pos.x() / self.zoom[0]), int(pos.y() / self.zoom[1])
            if self.cursorINregion((mouse_x, mouse_y)):
                QApplication.setOverrideCursor(Qt.SizeAllCursor)

    def DetectPOS2(self):
        self.cursor_OUT = True
        QApplication.setOverrideCursor(Qt.ArrowCursor)

    def keyPressEvent(self, event):
        if self.toolSelected==1 and self.complete_selection and event.key()==Qt.Key_Delete:     #Delete selected image
            self.selection = self.Move = self.complete_selection = False
            image = CV.LoadImage("TP_assets/Backup.png")
            image = np.zeros((image.shape[0], image.shape[1], 3), np.uint8)
            image[:] = self.color_bg
            self.image = CV.OverlayImage(image, self.image, self.toolCoords)
            self.image_CVT = CV.OverlayImage(image, self.image_CVT, self.toolCoords)
            self.Render(self.image)
        elif self.toolSelected==8 and self.point:
            if event.key()==Qt.Key_Escape:
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.point = False
                self.TextEdit.hide()
                self.Render(self.image)

    def mousePressEvent(self, event):
        if self.toolSelected!=0:
            if event.button()==1:
                pos = self.background.mapFromGlobal(self.mapToGlobal(event.pos()))
                mouse_x, mouse_y = int(pos.x() / self.zoom[0]), int(pos.y() / self.zoom[1])
                if self.toolSelected==1:
                    if not self.selection:
                        CV.SaveImage("TP_assets/Backup.png", self.image)  #creating image backup
                        CV.SaveImage("TP_assets/Backup3.png", self.image_CVT)  # creating image backup for GrayScale
                        self.init_coords = (mouse_x, mouse_y)
                        self.selection = True
                    else:
                        if self.cursorINregion((mouse_x, mouse_y)):
                            self.Move = True
                            LR, UD, dst = CV.calcRegion((mouse_x, mouse_y, self.toolCoords[0], self.toolCoords[1]))
                            self.init_coords = (dst[0] * LR, dst[1] * UD)       # distance parameter instead of fixed point #moving de coord
                        else:
                            self.selection = self.Move = self.complete_selection = False
                            image = CV.LoadImage("TP_assets/Backup.png")
                            self.image = CV.OverlayImage(image, self.image, self.toolCoords)
                            image2 = CV.LoadImage("TP_assets/Backup3.png")
                            self.image_CVT = CV.OverlayImage(image2, self.image_CVT, self.toolCoords)
                            self.Render(self.image)
                elif self.toolSelected == 2 or self.toolSelected == 9:
                    self.init_coords = (mouse_x, mouse_y)
                elif 3<=self.toolSelected<= 7:
                    CV.SaveImage("TP_assets/Backup.png", self.image)  # creating image backup
                    CV.SaveImage("TP_assets/Backup3.png", self.image_CVT)  # creating image backup for GrayScale
                    self.init_coords = (mouse_x, mouse_y)
                elif self.toolSelected==8:
                    if not self.point:
                        CV.SaveImage("TP_assets/Backup.png", self.image)  # creating image backup
                        CV.SaveImage("TP_assets/Backup3.png", self.image_CVT)  # creating image backup for GrayScale
                        self.init_coords = (mouse_x, mouse_y)
                        self.point = True
                        self.TextEdit.move(self.init_coords[0], self.init_coords[1])
                        self.TextEdit.setText("Please Enter Here")
                        self.TextEdit.show()
                        self.UpdateText()
                    else:
                        self.point = False
                        CV.drawText(self.image, self.TextEdit.text(), self.init_coords, self.font[0], self.font[1], self.color, self.thickness)
                        CV.drawText(self.image_CVT, self.TextEdit.text(), self.init_coords, self.font[0], self.font[1], self.color, self.thickness)
                        self.TextEdit.hide()
                elif self.toolSelected == 10:
                    color = self.image[mouse_y, mouse_x]
                    self.color = (int(color[0]),int(color[1]), int(color[2]))
                    CV.Color_picker(self.color)
                    self.colorBtn.setIcon(QIcon("TP_assets/color.png"))

    def mouseReleaseEvent(self, event):
        if self.toolSelected != 0:
            if event.button()==1:
                pos = self.background.mapFromGlobal(self.mapToGlobal(event.pos()))
                mouse_x, mouse_y = int(pos.x() / self.zoom[0]), int(pos.y() / self.zoom[1])
                if self.toolSelected==1:
                    if self.selection:
                        if not self.Move and not self.complete_selection:
                            self.toolCoords = CV.ReLocateCoords([self.init_coords[0], self.init_coords[1], mouse_x, mouse_y])
                            image = CV.LoadImage("TP_assets/Backup.png")
                            CV.drawPrimitive(image, self.toolCoords, 1, None, int(2/max(self.zoom[0], self.zoom[1])))  # only using backup image to bit since temp
                            self.Render(image)
                            image = CV.CropImage(self.image, self.toolCoords)
                            CV.SaveImage("TP_assets/Backup.png",image)        # save cropped image
                            image2 = CV.CropImage(self.image_CVT, self.toolCoords)
                            CV.SaveImage("TP_assets/Backup3.png", image2)
                            CV.drawPrimitive(self.image, self.toolCoords, 5, (255, 255, 255), -1)       # make empty to selected region on base image
                            CV.SaveImage("TP_assets/Backup2.png", self.image)                                     # save image background w white hole
                            CV.drawPrimitive(self.image_CVT, self.toolCoords, 5, (255, 255, 255), -1)  # make empty to selected region on base image
                            self.complete_selection = True
                        else:   #moving cropped image
                            self.Move = False
                elif 3 <= self.toolSelected <= 7:
                    if self.thickness == -1 and 6 <= self.toolSelected <= 7:
                        CV.drawPrimitive(self.image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected + 2, self.color)
                        CV.drawPrimitive(self.image_CVT, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected + 2, self.color)
                    else:
                        CV.drawPrimitive(self.image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected, self.color, self.thickness)
                        CV.drawPrimitive(self.image_CVT, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected, self.color, self.thickness)
                    self.Render(self.image)
                    CV.SaveImage("TP_assets/Backup.png", self.image)
                    CV.SaveImage("TP_assets/Backup3.png", self.image_CVT)  # creating image backup for GrayScale

    def mouseMoveEvent(self, event):
        if self.cursor_OUT:
            return
        pos = self.background.mapFromGlobal(self.mapToGlobal(event.pos()))
        mouse_x, mouse_y = int(pos.x() / self.zoom[0]), int(pos.y() / self.zoom[1])
        if self.toolSelected==1:
            if self.selection:
                image = CV.LoadImage("TP_assets/Backup.png")
                if not self.Move and not self.complete_selection:
                    CV.drawPrimitive(image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 1, None, int(1/max(self.zoom[0], self.zoom[1])))  # only using backup image to render since temp
                    self.Render(image)
                else:
                    self.moveImage((mouse_x, mouse_y), image)
        elif self.toolSelected==2:
            CV.drawPrimitive(self.image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 3, self.color, self.thickness)
            CV.drawPrimitive(self.image_CVT, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 3, self.color, self.thickness)
            self.init_coords = (mouse_x, mouse_y)
            self.Render(self.image)
        elif 3<=self.toolSelected<=7:
            image = CV.LoadImage("TP_assets/Backup.png")
            if self.thickness==-1 and 6<=self.toolSelected<=7:
                CV.drawPrimitive(image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected+2, self.color)
            else:
                CV.drawPrimitive(image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected, self.color, self.thickness)
            self.Render(image)
        elif self.toolSelected==9:
            width = abs(self.thickness*2)
            CV.drawPrimitive(self.image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 3, self.color_bg, width)
            CV.drawPrimitive(self.image_CVT, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 3, self.color_bg, width)
            self.init_coords = (mouse_x, mouse_y)
            self.Render(self.image)
            CV.SaveImage("TP_assets/Backup.png", self.image)
            CV.SaveImage("TP_assets/Backup3.png", self.image_CVT)  # creating image backup for GrayScale
    def cursorINregion(self, mousepos):
        inregion = False
        if self.toolCoords[2] < self.toolCoords[0]:
            if self.toolCoords[2] <= mousepos[0]<=self.toolCoords[0]:
                inregion = True
        elif self.toolCoords[2] > self.toolCoords[0]:
            if self.toolCoords[0] <= mousepos[0] <= self.toolCoords[2]:
                inregion = True
        if inregion:
            inregion = False
            if self.toolCoords[3] < self.toolCoords[1]:
                if self.toolCoords[3] <= mousepos[1]<=self.toolCoords[1]:
                    inregion = True
            elif self.toolCoords[3] > self.toolCoords[1]:
                if self.toolCoords[1] <= mousepos[1] <= self.toolCoords[3]:
                    inregion = True
        return inregion

    def SliderWidget(self, ott, default, min, max, width, action):
        slider = QSlider(self)
        slider.setOrientation(ott)
        slider.setValue(default)
        slider.setMinimum(min)
        slider.setMaximum(max)
        slider.setFixedWidth(width)
        slider.valueChanged.connect(action)
        slider.setStyleSheet("QSlider::groove:horizontal {border: 1px solid #bbb;background: white;height: 10px;border-radius: 4px;}"
                             "QSlider::sub-page:horizontal {background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,stop: 0 #66e, stop: 1 #bbf);background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,stop: 0 #bbf, stop: 1 #55f);border: 1px solid #777;height: 10px;border-radius: 4px;}"
                             "QSlider::add-page:horizontal {background: #fff;border: 1px solid #777;height: 10px;border-radius: 4px;}"
                             "QSlider::handle:horizontal {background: qlineargradient(x1:0, y1:0, x2:1, y2:1,stop:0 #eee, stop:1 #ccc);border: 1px solid #777;width: 13px;margin-top: -2px;margin-bottom: -2px;border-radius: 4px;}"
                             "QSlider::handle:horizontal:hover {background: qlineargradient(x1:0, y1:0, x2:1, y2:1,stop:0 #fff, stop:1 #ddd);border: 1px solid #444;border-radius: 4px;}"
                             "QSlider::sub-page:horizontal:disabled {background: #bbb;border-color: #999;}"
                             "QSlider::add-page:horizontal:disabled {background: #eee;border-color: #999;}"
                             "QSlider::handle:horizontal:disabled {background: #eee;border: 1px solid #aaa;border-radius: 4px;}")
        return slider

    def Label_TextOnly(self, text, font=None):
        label_Text = QLabel(self)
        label_Text.setText(text)
        if font:
            label_Text.setFont(QFont(font[0], font[1]))
        return label_Text

    def PushBtnIcon(self, icon, action):
        btn = QPushButton(self)
        btn.setIcon(QIcon(icon))
        btn.setStyleSheet('border:0')
        btn.clicked.connect(action)
        return btn

    def PushBtnText(self, text, action, font=None):
        btn = QPushButton(self)
        btn.setText(text)
        if font:
            btn.setFont(QFont(font[0], font[1]))
        btn.clicked.connect(action)
        return btn

    def zoomTool(self, zoom):
        if self.new:
            self.zoom_slider.setValue(100)
            return
        self.scrollArea.setWidgetResizable(False)
        self.CleanSelectedRegion()
        if zoom==1:
            self.zoom[0] = self.zoom_slider.value() / 100
        else:
            if zoom==2:
                if self.zoom[0]<5:
                    self.zoom[0] += 0.01
            elif zoom==3:
                if self.zoom[0]>0.01:
                    self.zoom[0] -= 0.01
            elif zoom==4:   # actual size
                self.zoom[0] = 1
            self.zoom_slider.setValue(int(self.zoom[0] * 100))
        self.zoom_percentage.setText("\t" + str(int(self.zoom[0] * 100)) + "%")
        self.zoom[1] = self.zoom[0]
        if zoom==5: # fitscreen
            self.scrollArea.setWidgetResizable(True)
            print(self.background.size())
            img_w, img_h = self.image.shape[1], self.image.shape[0]
            screen_w, screen_h = self.background.size().width(), self.background.size().height()
            if img_w>screen_w:
                self.zoom[0] = screen_w/img_w
            elif img_w<screen_w:
                self.zoom[0] = img_w/screen_w
            if img_h>screen_h:
                self.zoom[1] = screen_h/img_h
            elif img_h<screen_h:
                self.zoom[1] = img_h/screen_h
            self.zoom_slider.setValue(100)
            self.zoom_percentage.setText("\t" + str(100) + "%")
        self.Render(self.image)

    def moveImage(self, mousepos, image):
        new_coord = (mousepos[0]+self.init_coords[0], mousepos[1]+self.init_coords[1])
        self.toolCoords = [new_coord[0], new_coord[1], new_coord[0]+image.shape[1], new_coord[1]+image.shape[0]]
        CV.drawPrimitive(image, (0,0,image.shape[1]-1, image.shape[0]-1), 1, None, int(2 / max(self.zoom[0], self.zoom[1])))  # only using backup image to bit since temp   #dash line
        temp_image = CV.LoadImage("TP_assets/Backup2.png")
        temp_image = CV.OverlayImage(image, temp_image, self.toolCoords)
        self.Render(temp_image)

    def Menubars(self):
        menu_list = [self.MenuDetail('&New', 'New Page', lambda :self.resizeDialog(True), 'Ctrl+N', 'TP_assets/new.jpg'),                        # New
                    self.MenuDetail('&Open', 'Open New Project', lambda :self.fileDialog(1), 'Ctrl+O', 'TP_assets/open.jpg'),    # Open
                    self.MenuDetail('&Save', 'Save Project', lambda :self.fileDialog(2), 'Ctrl+S', 'TP_assets/save.png'),      # Save
                    self.MenuDetail('&Exit', 'Quit Application', self.QuitDialog, 'Shift+Esc', 'TP_assets/exit.png')]           # Exit
        screen_list = [self.MenuDetail('Actual Size', 'Zoom to 100%', lambda : self.zoomTool(4)),
                        self.MenuDetail('Fit Screen', 'Zoom to fit screen', lambda: self.zoomTool(5))]
        self.grid_list = [self.MenuDetail('None', 'default without gridline', lambda : self.grid_option(0), checked=True),
                            self.MenuDetail('Standard', '3x3 grid', lambda : self.grid_option(1)),
                            self.MenuDetail('Detailed', '10x10 pixels', lambda : self.grid_option(2))]
        self.status_show = self.MenuDetail('Status bar', 'show / hide status bar', lambda : self.ShowHide(1), checked=True)
        self.toolbar_show = self.MenuDetail('Toolbar', 'show / hide toolbar', lambda : self.ShowHide(2), checked=True)
        about_help = self.MenuDetail('About', 'About the application', self.about)
        menu = self.menuBar()
        fileMenu = menu.addMenu('&File')
        viewMenu = menu.addMenu('&View')
        helpMenu = menu.addMenu('&Help')
        for menu in menu_list:
            fileMenu.addAction(menu)
        screenMenu = viewMenu.addMenu('Screen')
        for screen in screen_list:
            screenMenu.addAction(screen)
        gridMenu = viewMenu.addMenu('Gridlines')
        for grid in self.grid_list:
            gridMenu.addAction(grid)
        viewMenu.addAction(self.toolbar_show)
        viewMenu.addAction(self.status_show)
        helpMenu.addAction(about_help)

    def MenuDetail(self, name, statusTip, action=None, shortcutKey=None, icon=None, checked = None):
        if icon:
            MenuAct = QAction(QIcon(icon),name,self)
        else:
            MenuAct = QAction(name, self)
        if shortcutKey:
            MenuAct.setShortcut(shortcutKey)
        MenuAct.setStatusTip(statusTip)
        if action:
            MenuAct.triggered.connect(action)
        if checked:
            MenuAct.setCheckable(True)
            MenuAct.setChecked(True)
        return MenuAct

    def Toolbars(self):
        self.SelectionTool = self.ToolButton('TP_assets/selection.png', 'Selection', lambda :self.ToolSelection(1))    #Selection
        slc_tool = [self.ToolDetail('TP_assets/crop.jpg', 'Crop', self.CropTool),  # Crop
                    self.ToolDetail('TP_assets/resize.png', 'Resize', self.resizeDialog)]  # Resize                ########### nt yet do
        tools_tool = [self.ToolButton('TP_assets/draw.png', 'Draw', lambda: self.ToolSelection(2)),  # Draw
                    self.ToolButton('TP_assets/eraser.png', 'Eraser', lambda: self.ToolSelection(9)),  # Eraser
                    self.ToolButton('TP_assets/dropper.png', 'Color Picker', lambda: self.ToolSelection(10)),  # Dropper
                    self.ToolButton('TP_assets/text.png', 'Text', lambda: self.ToolSelection(8))]  # Text
        shape_tool = [self.ToolButton('TP_assets/line.png', 'Line', lambda: self.ToolSelection(3)),  # Line
                    self.ToolButton('TP_assets/circle.png', 'Circle', lambda: self.ToolSelection(4)),  # Circle
                    self.ToolButton('TP_assets/rect.png', 'Rectangle', lambda: self.ToolSelection(5)),  # Rect
                    self.ToolButton('TP_assets/triangle.png', 'Triangle', lambda: self.ToolSelection(6)),  # Triangle
                    self.ToolButton('TP_assets/diamond.png', 'Diamond', lambda: self.ToolSelection(7))]  # Diamond
        Rot_combo_str = ["Rotate","Rot_Right90"+u'\N{DEGREE SIGN}', "Rot_Left  90"+u'\N{DEGREE SIGN}', "Rotate 180"+u'\N{DEGREE SIGN}', "Flip Vertical", "Flip Horizontal"]
        Rot_combo_icon = ["TP_assets/rot.png", "TP_assets/rot_right.png", "TP_assets/rot_left.png", "TP_assets/rot_half.png", "TP_assets/flip_v.png", "TP_assets/flip_h.png"]
        comboRot = self.ComboBoxDetail(True, Rot_combo_str, Rot_combo_icon, "Rotation", (115,30), lambda :self.ComboRotation(comboRot))
        font_combo_str = ["HersheyComplex", "Her_Complex(S)", "HersheyDuplex", "HersheyPlain", "HersheyScript(C)", "HersheyScript(S)", "HersheyTriplex", "Italic"]
        self.fontStyle = self.ComboBoxDetail(False, font_combo_str, None, "Font Style", (115,30), self.FontStyle_Update)
        size_combo_str = ["1px", "2px", "3px", "4px", "5px", "6px", "7px", "8px", "9px", "10p"]
        size_combo_icon = ["TP_assets/1px.png", "TP_assets/2px.png", "TP_assets/3px.png", "TP_assets/4px.png", "TP_assets/5px.png", "TP_assets/6px.png", "TP_assets/7px.png", "TP_assets/8px.png", "TP_assets/9px.png", "TP_assets/10px.png"]
        self.comboSize = self.ComboBoxDetail(True, size_combo_str, size_combo_icon, "Thickness", (75,30), lambda :self.Outline_Fill(True), (38,30))

        self.fontSize = QLineEdit(self)
        self.fontSize.setValidator(QDoubleValidator())
        self.fontSize.setFixedSize(25, 30)
        self.fontSize.setText("1.0")
        self.fontSize.textChanged.connect(self.FontStyle_Update)
        self.option_btn = self.ToolButton('TP_assets/outline.png', "Outline", self.Outline_Fill, 1, (80,35))
        self.colorBtn = self.ToolButton('TP_assets/color2.png', "Edit Color", lambda: self.colorDialog(True), 2)
        ColCvt_combo_str = ["RGB image", "Grayscale image", "HSV image", "Hue channel", "Saturation channel", "Value channel", "HSL image", "Light channel", "CIE_L*A*B image", "LUV image", "YCrCb JPEG", "CIE_XYZ image"]
        ColCvt_combo_icon = ["TP_assets/rgb.png", "TP_assets/gray.png", "TP_assets/hsv.png", "TP_assets/hsv2.png", "TP_assets/hsv2.png", "TP_assets/hsv2.png", "TP_assets/hsv.png", "TP_assets/hsv2.png", "TP_assets/hsv.png", "TP_assets/hsv.png", "TP_assets/hsv.png", "TP_assets/hsv.png"]
        ColCvt_combo = self.ComboBoxDetail(True, ColCvt_combo_str, ColCvt_combo_icon, "Color Conversion", (165,30), lambda :self.Color_Conversion(ColCvt_combo))
        self.toolbar = QToolBar("Toolbar")
        self.addToolBar(self.toolbar)
        self.toolbar.addWidget(self.SelectionTool)
        for tool in slc_tool:
            self.toolbar.addAction(tool)
        self.toolbar.addWidget(comboRot)
        self.toolbar.addSeparator()
        for tool in tools_tool:
            self.toolbar.addWidget(tool)
        self.toolbar.addWidget(self.fontStyle)
        self.toolbar.addWidget(self.fontSize)
        self.toolbar.addSeparator()
        for tool in shape_tool:
            self.toolbar.addWidget(tool)
        self.toolbar.addWidget(self.option_btn)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.comboSize)
        self.toolbar.addWidget(self.colorBtn)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(ColCvt_combo)
        self.toolbar.setEnabled(False)
        tracker2 = MouseTracker(self.toolbar)
        tracker2.positionChanged.connect(self.DetectPOS2)

    def ToolButton(self, icon, name, action, flag=None, icon_size=None):
        ToolBtn = QToolButton(self)
        ToolBtn.setIcon(QIcon(icon))
        ToolBtn.setToolTip(name)
        ToolBtn.clicked.connect(action)
        if icon_size:
            ToolBtn.setFixedSize(icon_size[0], icon_size[1])
        if flag==1:
            ToolBtn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            ToolBtn.setText(name)
            return ToolBtn
        elif flag==2:
            return ToolBtn
        ToolBtn.setCheckable(True)
        ToolBtn.setAutoExclusive(True)
        return ToolBtn

    def UpdateText(self):
        image = CV.LoadImage("TP_assets/Backup.png")
        CV.drawText(image, self.TextEdit.text(), self.init_coords, self.font[0], self.font[1], self.color, self.thickness)
        self.Render(image)

    def FontStyle_Update(self):
        if not self.toolSelected==8:
            return
        self.font[0] = self.fontStyle.currentIndex()
        if self.fontSize.text()=="":
            self.fontSize.setText("0.1")
        self.font[1] = float(self.fontSize.text())
        self.UpdateText()

    def ShowHide(self, flag):
        if flag==1: #status
            if self.status_show.isChecked():
                self.statusBar().show()
            else:
                self.statusBar().hide()
        elif flag==2:   #toolbar
            if self.toolbar_show.isChecked():
                self.toolbar.show()
            else:
                self.toolbar.hide()

    def ComboBoxDetail(self, icon, combo_str, combo_icon, name, size, action, icon_size=None):
        combo = QComboBox(self)
        combo.setToolTip(name)
        combo.setFixedSize(size[0], size[1])
        if icon:
            for r in range(len(combo_icon)):
                combo.addItem(QIcon(combo_icon[r]), combo_str[r])
                if icon_size:
                    combo.setIconSize(QSize(icon_size[0], icon_size[1]))
        else:
            for f in combo_str:
                combo.addItem(f)
        if action:
            combo.currentIndexChanged.connect(action)
        return combo

    def ComboRotation(self, comboRot):
        index = comboRot.currentIndex()
        if index == 0 or self.new:
            comboRot.setCurrentIndex(0)
            return
        comboRot.blockSignals(True)
        if self.selection:
            image = CV.LoadImage("TP_assets/Backup.png")  # load cropped image by selection
            temp_image = CV.LoadImage("TP_assets/Backup2.png")
            image2 = CV.LoadImage("TP_assets/Backup3.png")

            image2, _ = CV.RotateImage(image2, self.toolCoords, index)
            image, self.toolCoords = CV.RotateImage(image, self.toolCoords, index)
            CV.SaveImage("TP_assets/Backup.png", image)       # renew n save latest image
            CV.SaveImage("TP_assets/Backup3.png", image2)  # renew n save latest image
            CV.drawPrimitive(image, (0, 0, image.shape[1] - 1, image.shape[0] - 1), 1, None, int(2 / max(self.zoom[0], self.zoom[1])))  # only using backup image to bit since temp   #dash line

            temp_image = CV.OverlayImage(image, temp_image, self.toolCoords)
        else:
            self.image, self.toolCoords = CV.RotateImage(self.image, (0,0,self.image.shape[1], self.image.shape[0]), index)
            self.image_CVT, _ = CV.RotateImage(self.image_CVT, (0,0,self.image_CVT.shape[1], self.image_CVT.shape[0]), index)
            temp_image = self.image
        self.Render(temp_image)
        comboRot.setCurrentIndex(0)
        comboRot.blockSignals(False)

    def ToolDetail(self, icon, name, action):
        ToolAct = QAction(QIcon(icon), name, self)
        ToolAct.triggered.connect(action)
        return ToolAct

    def ToolSelection(self, slc):
        if self.new:
            return
        self.CleanSelectedRegion()
        self.toolSelected = slc
        if self.toolSelected==2 or self.toolSelected==3 or 8<=self.toolSelected<=10:
            self.Outline_Fill()

    def CleanSelectedRegion(self):
        if self.toolSelected == 1 and self.selection:
            self.selection = self.Move = self.complete_selection =False
            image = CV.LoadImage("TP_assets/Backup.png")
            self.image = CV.OverlayImage(image, self.image, self.toolCoords)
            image2 = CV.LoadImage("TP_assets/Backup3.png")
            self.image_CVT = CV.OverlayImage(image2, self.image_CVT, self.toolCoords)

    def Color_Conversion(self, combo):
        if self.new:
            combo.setCurrentIndex(0)
            return
        self.CleanSelectedRegion()
        self.image = CV.ConvertColor(combo.currentIndex(), self.image_CVT)
        self.Render(self.image)

    def Outline_Fill(self, flag=None):
        if flag:
            self.thickness = self.comboSize.currentIndex()+1
        else:
            if self.thickness!=-1 and 4<=self.toolSelected<=7:
                self.option_btn.setText("Fill")
                self.option_btn.setIcon(QIcon('TP_assets/fill.png'))
                self.thickness = -1
            else:
                self.option_btn.setText("Outline")
                self.option_btn.setIcon(QIcon('TP_assets/outline.png'))
                self.thickness = self.comboSize.currentIndex()+1
        if self.point:
            self.UpdateText()

    def CropTool(self):
        if not self.selection:
            return
        self.image = CV.LoadImage("TP_assets/Backup.png")
        self.Render(self.image)
        self.image_CVT = CV.LoadImage("TP_assets/Backup3.png")    #

    def HV_input(self, hv):
        if self.Aspc_ratio:
            if hv=='h':
                self.v_input.setText(self.h_input.text())
            elif hv=='v':
                self.h_input.setText(self.v_input.text())

    def By_resize(self):
        if self.by_2.isChecked():
            self.resize_value[0], self.resize_value[1] = self.h_input.text(), self.v_input.text()
            self.h_input.blockSignals(True)
            self.v_input.blockSignals(True)
            self.h_input.setText(str(self.resize_value[2]))
            self.v_input.setText(str(self.resize_value[3]))
            self.h_input.blockSignals(False)
            self.v_input.blockSignals(False)
        elif self.by_1.isChecked():
            self.resize_value[2], self.resize_value[3] = self.h_input.text(), self.v_input.text()
            self.h_input.blockSignals(True)
            self.v_input.blockSignals(True)
            self.h_input.setText(str(self.resize_value[0]))
            self.v_input.setText(str(self.resize_value[1]))
            self.h_input.blockSignals(False)
            self.v_input.blockSignals(False)

    def AspectRatio(self):
        if self.Aspc_ratio:
            self.Aspc_ratio = False
        else:
            self.Aspc_ratio = True
    def resizeOption(self, dlg, flag=None):
        dlg.close()
        w, h = int(self.h_input.text()), int(self.v_input.text())
        if w==0:
            w = 1
        if h==0:
            h = 1
        if flag:    # new page
            self.image = CV.ResizeImage(self.image, (w, h))
            self.colorDialog()
            return
        if self.selection:
            image = CV.LoadImage("TP_assets/Backup.png")
            image2 = CV.LoadImage("TP_assets/Backup3.png")
        else:
            image = self.image
            image2 = self.image_CVT
        if self.by_1.isChecked():
            w, h = int(w / 100 * image.shape[1]), int(h / 100 * image.shape[0])
            image = CV.ResizeImage(image, (w, h))
            image2 = CV.ResizeImage(image2, (w, h))
        else:
            image = CV.ResizeImage(image, (w, h))
            image2 = CV.ResizeImage(image2, (w, h))
        CV.SaveImage("TP_assets/Backup.png", image)
        CV.SaveImage("TP_assets/Backup3.png", image2)
        if not self.selection:
            self.image = image
            self.image_CVT = image2
        else:
            CV.drawPrimitive(image, (0, 0, image.shape[1] - 1, image.shape[0] - 1), 1, None, int(2 / max(self.zoom[0], self.zoom[1])))  # only using backup image to bit since temp   #dash line
            temp_image = CV.LoadImage("TP_assets/Backup2.png")
            center = self.toolCoords[0]+(self.toolCoords[2]-self.toolCoords[0])//2, self.toolCoords[1]+(self.toolCoords[3]-self.toolCoords[1])//2
            self.toolCoords = [center[0]-w//2, center[1]-h//2, center[0]+w//2, center[1]+h//2]
            image = CV.OverlayImage(image, temp_image, self.toolCoords)
        self.Render(image)
        self.Aspc_ratio = True

    def resizeDialog(self, flag=None):
        if flag:    # New Page
            self.image = np.zeros((500, 500, 3), np.uint8)
        if self.selection:
            image = CV.LoadImage("TP_assets/Backup.png")
            self.resize_value[2], self.resize_value[3] = image.shape[1], image.shape[0]
        else:
            self.resize_value[2], self.resize_value[3] = self.image.shape[1], self.image.shape[0]
        dlg = QDialog(self)
        dlg.setWindowModality(Qt.ApplicationModal)
        if flag:
            dlg.setWindowTitle("Dimension")
        else:
            dlg.setWindowTitle("Resize")
        dlg.setFixedSize(300,250)
        main_layout = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        if flag:
            text1 = self.Label_TextOnly("By pixels:", ('Times New Roman', 12))
            layout1.addWidget(text1)
        else:
            text1 = self.Label_TextOnly("By: ", ('Times New Roman', 12))
            layout1.addWidget(text1)
            layout1.addStretch(1)
            self.by_1 = QRadioButton(self)
            self.by_1.setText("Percentage")
            self.by_1.setFont(QFont('Times New Roman', 11))
            self.by_1.setChecked(True)
            layout1.addWidget(self.by_1)
            layout1.addStretch(1)
            self.by_2 = QRadioButton(self)
            self.by_2.setText("Pixel    ")
            self.by_2.setFont(QFont('Times New Roman', 11))
            self.by_2.toggled.connect(self.By_resize)
            layout1.addWidget(self.by_2)
        h_label = QLabel(self)
        h_label.setPixmap(QPixmap("TP_assets/horizontal.png"))
        layout2.addWidget(h_label)
        layout2.addStretch(1)
        h_text = self.Label_TextOnly("Horizontal :", ('Times New Roman', 11))
        layout2.addWidget(h_text)
        layout2.addStretch(1)
        self.h_input = QLineEdit(self)
        onlyInt = QIntValidator()
        self.h_input.setValidator(onlyInt)
        self.h_input.setFixedSize(60, 30)
        if flag:
            self.h_input.setText("500")
        else:
            self.h_input.setText("100")
        self.h_input.textChanged.connect(lambda :self.HV_input('h'))
        layout2.addWidget(self.h_input)
        v_label = QLabel(self)
        v_label.setPixmap(QPixmap("TP_assets/vertical.png"))
        layout3.addWidget(v_label)
        layout3.addStretch(1)
        v_text = self.Label_TextOnly("Vertical :", ('Times New Roman', 11))
        layout3.addWidget(v_text)
        layout3.addStretch(1)
        self.v_input = QLineEdit(self)
        onlyInt = QIntValidator()
        self.v_input.setValidator(onlyInt)
        self.v_input.setFixedSize(60, 30)
        if flag:
            self.v_input.setText("500")
        else:
            self.v_input.setText("100")
        self.v_input.textChanged.connect(lambda :self.HV_input('v'))
        layout3.addWidget(self.v_input)
        ratio_check = QCheckBox(self)
        ratio_check.setChecked(True)
        ratio_check.setText("Maintain aspect ratio")
        ratio_check.stateChanged.connect(self.AspectRatio)
        option_btn = self.PushBtnText("APPLY", lambda : self.resizeOption(dlg, flag))
        main_layout.addLayout(layout1)
        main_layout.addStretch(1)
        main_layout.addLayout(layout2)
        main_layout.addLayout(layout3)
        main_layout.addStretch(1)
        main_layout.addWidget(ratio_check)
        main_layout.addWidget(option_btn)
        dlg.setLayout(main_layout)
        dlg.exec_()

    def newLAUNCH(self):
        self.selection = self.Move = self.complete_selection = False
        self.zoomTool(4)
        self.Render(self.image)
        for atr in self.grid_list:
            atr.setCheckable(True)

    def colorDialog(self, flag=None):
        dlg = QColorDialog(self)
        dlg.setWindowModality(Qt.ApplicationModal)
        col = QColorDialog.getColor()
        if col.isValid():
            if flag:
                self.color = tuple(reversed(col.getRgb()[:3]))
                CV.Color_picker(self.color)
                self.colorBtn.setIcon(QIcon("TP_assets/color.png"))
                if self.point:
                    self.UpdateText()
            else:
                if self.new:
                    self.new = False
                    self.toolbar.setEnabled(True)
                self.color_bg = tuple(reversed(col.getRgb()[:3]))
                self.image[:] = self.color_bg
                self.image_CVT = self.image

                self.newLAUNCH()

    def fileDialog(self, flag):
        filter = "Images (*.png *.jpg)"
        if flag==1:     #open
            file, _ = QFileDialog.getOpenFileName(self, "File Directory", QDir.currentPath(), filter)
            if file == (""):
                return
            if self.new:
                self.new = False
                self.toolbar.setEnabled(True)
            self.color_bg = (255, 255, 255)
            self.image = CV.LoadImage(file)
            self.image_CVT = CV.LoadImage(file) # creating image backup for Conversion
            self.newLAUNCH()
        elif flag==2:   #save
            file, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.currentPath(), "PNG(*.png);;JPEG(*.jpg *.jpeg)")
            if file == ("") or self.new:
                return
            status = CV.SaveImage(file, self.image)
            if status:
                self.InfoDialog(file)

    def InfoDialog(self, filepath):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText("Your Project is compiled and saved successfully")
        msg.setWindowTitle("File Saved")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDetailedText("The filepath is as follow:\n"+filepath)
        msg.exec_()

    def QuitDialog(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Are you sure to quit application")
        msg.setInformativeText("Reminder: Save your project before quit")
        msg.setWindowTitle("Quit")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        quit = msg.exec_()
        if quit==16384:
            sys.exit()

    def grid_option(self, value):
        if self.new:
            return
        for grid in self.grid_list:
            grid.setChecked(False)
        self.grid_list[value].setChecked(True)

        self.grid = value
        self.Render(self.image)

    def Grid(self, image):
        CV.SaveImage("TP_assets/Backup_Last.png", image)      # create backup to save last action
        image = CV.LoadImage("TP_assets/Backup_Last.png")
        if self.grid == 1:   # 3x3grid
            CV.drawPrimitive(image, (0, image.shape[0] // 3, image.shape[1], image.shape[0] // 3), 3, (123, 123, 123), 1)
            CV.drawPrimitive(image, (0, image.shape[0] // 3 * 2, image.shape[1], image.shape[0] // 3 * 2), 3, (123, 123, 123), 1)
            CV.drawPrimitive(image, (image.shape[1]//3, 0, image.shape[1]//3, image.shape[0]), 3, (123, 123, 123), 1)
            CV.drawPrimitive(image, (image.shape[1]//3*2, 0, image.shape[1]//3*2, image.shape[0]), 3, (123, 123, 123), 1)
        elif self.grid == 2: # 10x10px
            for i in range(1, int(image.shape[1]/10)+1):
                CV.drawPrimitive(image, (10*i, 0, 10*i, image.shape[0]), 2, (150, 150, 150), 1)
            for i in range(1, int(image.shape[0]/10)+1):
                CV.drawPrimitive(image, (0, 10*i, image.shape[1], 10*i), 2, (150, 150, 150), 1)
        return image

    def Render(self, image):
        image = self.Grid(image)
        image_RGBA = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        QtImg = QImage(image_RGBA.data, image_RGBA.shape[1], image_RGBA.shape[0], QImage.Format_ARGB32)
        # Display the image to the label;
        # self.background.setPixmap(QPixmap.fromImage(QtImg))
        self.background.setPixmap(QPixmap.scaled(QPixmap.fromImage(QtImg), int(image.shape[1]*self.zoom[0]), int(image.shape[0]*self.zoom[1]), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.background.resize(int(image.shape[1]*self.zoom[0]), int(image.shape[0]*self.zoom[1]))
        self.pixel_dim.setText("Dimension : "+str(image.shape[1])+" x "+str(image.shape[0])+'px\t')

    def about(self):
        msg = QDialog(self)
        msg.setWindowTitle("ABOUT Tooth Paint")
        about_label = QLabel(self)
        about_label.setPixmap(QPixmap("TP_assets/about.png"))
        layout = QVBoxLayout(self)
        layout.addWidget(about_label)
        msg.setLayout(layout)
        msg.exec_()

    def SplashScreen(self):
        splash = QSplashScreen(QPixmap("TP_assets/splashscreen.png"), Qt.WindowStaysOnTopHint)
        splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        splash.setEnabled(False)

        progress_bar = QProgressBar(splash)
        progress_bar.setStyleSheet("QProgressBar {border: 1px solid black;text-align: top;padding: 2px;border-radius: 7px;"
                                   "background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #fff,stop: 0.4999 #eee,stop: 0.5 #ddd,stop: 1 #eee );height: 11px}"
                                   "QProgressBar::chunk {background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0,stop: 0 #ea00ff,stop: 1 #68fdff );"
                                   "border-top-left-radius: 7px;border-radius: 7px;border: None;}")
        progress_bar.setFixedWidth(530)
        progress_bar.move(120, 570)

        Loading_text = QLabel(splash)
        Loading_text.setFont(QFont("Calibri", 11))
        Loading_text.setStyleSheet("QLabel { background-color : None; color : #c12cff; }")
        Loading_text.setGeometry(125, 585, 300, 50)
        text = ("Initializing...", "Getting path...", "Measuring memory...", "Scanning for plugs in...", "Initializing panels...", "Loading library...", "Building color conversion tables...", "Reading tools...", "Reading Preferences...", "Getting ready...")
        splash.show()
        for i in range(0, 101):
            if i < 20:
                Loading_text.setText(text[0])
            elif i < 28:
                Loading_text.setText(text[1])
            elif i < 34:
                Loading_text.setText(text[2])
            elif i < 45:
                Loading_text.setText(text[3])
            elif i < 53:
                Loading_text.setText(text[4])
            elif i < 60:
                Loading_text.setText(text[5])
            elif i < 68:
                Loading_text.setText(text[6])
            elif i < 75:
                Loading_text.setText(text[7])
            elif i < 89:
                Loading_text.setText(text[8])
            else:
                Loading_text.setText(text[9])
            progress_bar.setValue(i)
            t = time.time()
            while time.time() < t + 0.035:
                QApplication.processEvents()
        time.sleep(1)

class VLine(QFrame):
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine|self.Sunken)

class MouseTracker(QObject):
    positionChanged = pyqtSignal(QPoint)

    def __init__(self, widget):
        super().__init__(widget)
        self._widget = widget
        self.widget.setMouseTracking(True)
        self.widget.installEventFilter(self)

    @property
    def widget(self):
        return self._widget

    def eventFilter(self, o, e):
        if o is self.widget and e.type() == QEvent.MouseMove:
            self.positionChanged.emit(e.pos())
        return super().eventFilter(o, e)

def main():
    app = QApplication(sys.argv)
    win = Paint()
    win.show()
    sys.exit(app.exec_())



if __name__=='__main__':
    main()

