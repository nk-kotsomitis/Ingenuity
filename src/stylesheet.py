STYLESHEET = """ 
    QMainWindow#mainPanel 
    {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffffff, stop: 1 #dee2e6);
        /* background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ccd0cf, stop: 1 #9ba8ab); */
    }
    
    QFrame#mainFrame
    {
        border: 5px solid white;
        border-radius: 20px;
        background: white;
    }
    
    QFrame#secondFrame
    {
        border: 5px solid white;
        border-radius: 20px;
        background: white;
    }
    
    QPushButton#mainButtons 
    {
        border-color: black;
        border-radius: 10px;
        padding: 5px;
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #253745, stop: 1 #4a5c6a);
        border: 1px solid black;
        font-size: 18px;
        color: #a7b4be;
    }
    
    QPushButton:disabled#mainButtons
    {
        background-color: #b0b0b0;
        color: #808080;
        border: 1px solid #909090;
    }
    
    QPushButton::hover#mainButtons 
    {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #3d5260, stop: 1 #627b8b);
        color: black;
    }
    
    QScrollArea#logsArea
    {
        
    }
    
    QTextEdit#logsText
    {
        border: 1px solid white;
        background: 'white';
        color: #cb353637;
        font-size: 14px;
    }
    
    QTabWidget::tab-bar 
    {
        alignment: left;
    }
    
    QTabBar::tab 
    {
        font-size: 14px;
        width: 200px;
        height: 40px;
    }
       
    QProgressBar 
    {
        background-color: #ffffff;
        border: 1px solid #ffffff; 
        border-radius: 5px;  
        height: 1px;
    }
    
    QProgressBar::chunk 
    {
        background-color: #4a5c6a;
    }
    
"""