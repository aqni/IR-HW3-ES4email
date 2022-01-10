from tkinter import*
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from query import MailSearch
from build_indexes import indexName


class FixedLabel(Label):
    def __init__(self, master=None, text=None):
        super().__init__(master, text=text, width=12, anchor=NW,)


class FixedEntry(Entry):
    def __init__(self, master=None):
        super().__init__(master, width=50,)


class ShouldOptionMenu(OptionMenu):
    OPTIONS = [None, "should", "must", "must_not"]

    def __init__(self, master=None):
        self.variable = StringVar(value=ShouldOptionMenu.OPTIONS[0])
        super().__init__(master, self.variable, *ShouldOptionMenu.OPTIONS)
        self.master = master  # 设置子类属性

    def getShould(self):
        return self.variable.get()


class MatchOptionMenu(OptionMenu):
    OPTIONS = ["match", "term", "fuzzy", "wildcard", "regexp", "prefix"]

    def __init__(self, master=None):
        self.variable = StringVar(value=MatchOptionMenu.OPTIONS[0])
        super().__init__(master, self.variable, *MatchOptionMenu.OPTIONS)
        self.master = master  # 设置子类属性

    def getMatch(self):
        return self.variable.get()


class KeywordForm(Frame):
    def __init__(self, master=None, name: str = None):
        super().__init__(master)
        self.master = master  # 设置子类属性
        self.name = name

        # set widget
        self.label = FixedLabel(self, text=name)
        self.entry = FixedEntry(self)
        self.match = MatchOptionMenu(self)
        self.should = ShouldOptionMenu(self)

        # set layout
        self.label.grid(row=0, column=0)
        self.entry.grid(row=0, column=1)
        self.match.grid(row=0, column=2)
        self.should.grid(row=0, column=3)

    def getQuery(self):
        query = {
            self.match.getMatch(): {
                self.name: self.entry.get()
            }
        } if self.entry.get() else None
        return self.should.getShould(), query


class TextForm(Frame):
    def __init__(self, master=None, name: str = None):
        super().__init__(master)
        self.master = master  # 设置子类属性
        self.name = name

        # set widget
        self.label = FixedLabel(self, text=name)
        self.entry = FixedEntry(self)
        self.should = ShouldOptionMenu(self)

        # set layout
        self.label.grid(row=0, column=0)
        self.entry.grid(row=0, column=1)
        self.should.grid(row=0, column=4)

    def getQuery(self):
        query = {
            "match": {
                self.name: self.entry.get()
            }
        } if self.entry.get() else None
        return self.should.getShould(), query


class IntRangeForm(Frame):
    def __init__(self, master=None, name: str = None):
        super().__init__(master)
        self.master = master  # 设置子类属性
        self.name = name

        # set widget
        self.label = FixedLabel(self, text=name)
        self.entryG = Spinbox(self, from_=0)
        self.gap = Label(self, text="-")
        self.entryL = Spinbox(self, from_=0)
        self.should = ShouldOptionMenu(self)

        # set layout
        self.label.grid(row=0, column=0)
        self.entryG.grid(row=0, column=1)
        self.gap.grid(row=0, column=2)
        self.entryL.grid(row=0, column=3)
        self.should.grid(row=0, column=4)

    def getQuery(self):
        query = {"range": {self.name: {}}}
        if self.entryG.get():
            query["range"][self.name]["gte"] = self.entryG.get()
        if self.entryL.get():
            query["range"][self.name]["lte"] = self.entryL.get()
        return self.should.getShould(), query if query["range"][self.name] else None


class DateRangeForm(Frame):
    def __init__(self, master=None, name: str = None):
        super().__init__(master)
        self.master = master  # 设置子类属性
        self.name = name

        # set widget
        self.label = FixedLabel(self, text=name)
        self.entryG = DateEntry(self)
        self.gap = Label(self, text="-")
        self.entryL = DateEntry(self)
        self.should = ShouldOptionMenu(self)

        # set layout
        self.label.grid(row=0, column=0)
        self.entryG.grid(row=0, column=1)
        self.gap.grid(row=0, column=2)
        self.entryL.grid(row=0, column=3)
        self.should.grid(row=0, column=4)

    def getQuery(self):
        query = {
            "range": {
                self.name: {
                    "gte": self.entryG.get_date().isoformat(),
                    "lte": self.entryL.get_date().isoformat(),
                }
            }
        }
        return self.should.getShould(), query


class SearchResult(Toplevel):
    COLUMNS = ("ID", "Date", "From", "To", "Subject", "length", "Body", "File")
    HEADERS = ("ID", "Date", "From", "To", "Subject", "length", "Body", "File")
    WIDTHES = (100,  100,     100,    100,  100,       100,      300,    100)

    def __init__(self, result: dict = None):
        super().__init__()
        if not result:
            return
        print(1)
        # set widget
        self.tv = ttk.Treeview(self, show="headings",
                               columns=SearchResult.COLUMNS,
                               height = 10)
        for (column, header, width) in zip(SearchResult.COLUMNS, SearchResult.HEADERS, SearchResult.WIDTHES):
            self.tv.column(column, width=width, anchor="w")
            self.tv.heading(column, text=header, anchor="w")
        # set data
        self.processResult(result)
        self.tv.pack()

        def treeviewClick(event):#单击
            print ('单击')
            for item in self.tv.selection():
                item_text = self.tv.item(item,"values")
                m=messagebox.showinfo(item_text[0],item_text[6])
                
        self.tv.bind('<ButtonRelease-1>', treeviewClick)

    def processResult(self,res:dict):
        self.title("Search result (total:"+str(res['hits']['total']['value'])+")")
        num=0
        for i,email in enumerate(res["hits"]["hits"]):
            num+=1
            if num>10:
                break
            data=email['_source']
            fromd=data['from.name']+'<'+data['from.address']+'>'
            tod=''
            for n,a in zip(data['to.name'],data['to.address']):
                tod+=n+'<'+a+'>'
            value=(data['Message-ID'],data['date'],fromd,tod,data['subject'],data['length'],data['body'],data['flie'])
            self.tv.insert('', i, values=value)

class SearchPanel(Tk):
    def __init__(self):
        super().__init__()
        self.title("Search mail")
        self.queryHelper = MailSearch(indexName)

        # set widget
        self.seatchBtn = Button(self, text="Start seatch", command=self.search)
        self.idForm = KeywordForm(self, "Message-ID")
        self.fileForm = KeywordForm(self, "flie")
        self.subjectForm = TextForm(self, "subject")
        self.bodyForm = TextForm(self, "body")
        self.lenForm = IntRangeForm(self, "length")
        self.dateForm = DateRangeForm(self, "date")
        self.fromNameForm = KeywordForm(self, "from.name")
        self.fromAddrFrom = KeywordForm(self, "from.address")
        self.toNameForm = KeywordForm(self, "to.name")
        self.toAddrForm = KeywordForm(self, "to.address")

        # set form
        self.allForm = [
            self.idForm, self.fileForm,
            self.subjectForm, self.bodyForm,
            self.dateForm, self.lenForm,
            self.fromNameForm, self.fromAddrFrom,
            self.toNameForm, self.toAddrForm,
        ]

        # set layout
        self.seatchBtn.grid(sticky='nw', padx=5)
        self.idForm.grid(sticky='nw', padx=5)
        self.fileForm.grid(sticky='nw', padx=5)
        self.subjectForm.grid(sticky='nw', padx=5)
        self.bodyForm.grid(sticky='nw', padx=5)
        self.lenForm.grid(sticky='nw', padx=5)
        self.dateForm.grid(sticky='nw', padx=5)
        self.fromNameForm.grid(sticky='nw', padx=5)
        self.fromAddrFrom.grid(sticky='nw', padx=5)
        self.toNameForm.grid(sticky='nw', padx=5)
        self.toAddrForm.grid(sticky='nw', padx=5)

    def getQuery(self) -> dict:
        result = {
            "bool": {
                "must": [],
                "must_not": [],
                "should": []
            }
        }
        for form in self.allForm:
            should, q = form.getQuery()
            if q and should and should !='None': #由于gui会自动将None转为‘None’,不处理会导致bug
                result["bool"][should].append(q)

        return result

    def search(self):
        query = self.getQuery()
        # print('search\n', query)
        res = self.queryHelper.searchMail(query)
        # print('res\n', res)
        SearchResult(res)

if __name__ == "__main__":
    SearchPanel().mainloop()
    