import gtk
from config import *

class MenuItemStock(gtk.ImageMenuItem):
    def __init__(self,stock_id,accel,laccel,mask=None):
	gtk.ImageMenuItem.__init__(self,stock_id=stock_id)
	if not mask:
	    self.add_accelerator("activate",accel,ord(laccel),
				 gtk.gdk.CONTROL_MASK,
				 gtk.ACCEL_VISIBLE)
	else:
	    self.add_accelerator("activate",accel,ord(laccel),
				 mask,
				 gtk.ACCEL_VISIBLE)

class MenuItem(gtk.ImageMenuItem):
    def __init__(self,name,accel,laccel,mask=None):
	gtk.ImageMenuItem.__init__(self,name)
	if not mask:
	    self.add_accelerator("activate",accel,ord(laccel),
				 gtk.gdk.CONTROL_MASK,
				 gtk.ACCEL_VISIBLE)
	else:
	    self.add_accelerator("activate",accel,ord(laccel),
				 mask,
				 gtk.ACCEL_VISIBLE)

class SubMenu(gtk.Menu):
    def __init__(self,accel_group):
        self.accel_group=accel_group
        gtk.Menu.__init__(self)
        self.items={}

    def add_item(self,key,label,laccel,mask=None):
        self.items[key]=MenuItem(label,self.accel_group,laccel,mask)
        self.append(self.items[key])

    def add_item_stock(self,key,stock_id,laccel,mask=None):
        self.items[key]=MenuItemStock(stock_id,self.accel_group,laccel,mask)
        self.append(self.items[key])

    def add_sub_menu(self,key,submenu):
        self.items[key].set_submenu(submenu)
        for k in submenu.items.keys():
            self.items[k]=submenu.items[k]

class MainMenu:
    __doc__="The main menu of an application.\nThe glade file must have only the label and not the full menu structure.\nYou can use the accel_group attribute to set a gtk.AccelGroup in the application"
    def __init__(self,xmlglade):
        self.accel_group=gtk.AccelGroup()
        self.menus={}
	self.xmlglade=xmlglade

    def add_menu(self,label,gladelabel,menuclass):
	m=self.xmlglade.get_widget(gladelabel)
	self.menus[label]=menuclass(self.accel_group)
	m.set_submenu(self.menus[label])
	self.menus[label].show_all()
        
    def connect(self,menu,item,function):
        self.menus[menu].items[item].connect("activate",function)

    __init__.__doc__=""
    add_menu.__doc__="Define a menu (a subclass of gtk.Menu) named label, linking it to\ngladelabel in the xmlglade specification."
    connect.__doc__="Connect the menu/item activate signal (i.e., the usual action\non a menu item) whit function."

class ContextMenu(gtk.Menu):
    def __init__(self):
	gtk.Menu.__init__(self)
	self.items={}

    def add_item(self,key,label):
	item=gtk.ImageMenuItem(label)
	self.items[key]=item
	self.append(item)
	item.show()

    def add_item_stock(self,key,stock_id):
	item=gtk.ImageMenuItem(stock_id=stock_id)
	self.items[key]=item
	self.append(item)
	item.show()

    def add_sub_menu(self,key,submenu):
        self.items[key].set_submenu(submenu)
        for k in submenu.items.keys():
            self.items[k]=submenu.items[k]

    def connect(self,item,function,data=None):
	if not data:
	    self.items[item].connect("activate",function)
	else:
	    self.items[item].connect("activate",function,data)

class MenuFile(SubMenu):
    def __init__(self,accel_group):
        SubMenu.__init__(self,accel_group)
        self.add_item_stock("save",gtk.STOCK_SAVE,'S')
        self.add_item_stock("saveas",gtk.STOCK_SAVE,'S',
                            mask=gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK)
        self.append(gtk.SeparatorMenuItem())        
        self.add_item_stock("quit",gtk.STOCK_QUIT,'Q')

class MenuGlossario(SubMenu):
    def __init__(self,accel_group):
        SubMenu.__init__(self,accel_group)
        self.add_item_stock("export","glossario-export",'X',
			    mask=gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK)
        self.add_item_stock("export_matrix","glossario-export-matrix",'X',
			    mask=gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK)
        self.add_item_stock("export_statistiche",
                            "glossario-export-statistiche",'X',
			    mask=gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK)
        self.add_item_stock("tex_categorie","glossario-categorie",'C',
                            mask=gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK)

class MenuVGlossario(MainMenu):
    def __init__(self,xmlglade):
	MainMenu.__init__(self,xmlglade)
	self.add_menu("file","menuFile",MenuFile)
	self.add_menu("glossario","menuGlossario",MenuGlossario)

class MenuFormeArabe(MainMenu):
    def __init__(self,xmlglade):
	MainMenu.__init__(self,xmlglade)
	self.add_menu("file","menuFile",MenuFile)

class MenuDivisioni(MainMenu):
    def __init__(self,xmlglade):
	MainMenu.__init__(self,xmlglade)
	self.add_menu("file","menuFile",MenuFile)

