import Pyro4
from Tkinter import *

class PhantomServer():

    def __init__(self):
        """
        Initializes the server
        """
        
        self.ns = Pyro4.naming.Nameserver

        frame = Frame(master)
        frame.pack()

        self.button = Button(frame, text="QUIT", fg="red", command=frame.quit)
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=LEFT)

        root =Tk()

        app = App(root)

		root.mainloop()


    def say_hi(self):
    	print "hi there, everyone!"