"""
# Stack overflow CLI
# Created by
# Gautam krishna R : www.github.com/gautamkrishnar
# And open source contributors at GitHub: https://github.com/gautamkrishnar/socli#contributors
"""

import getopt
import os
import sys
import urllib
import colorama
import requests
import urwid
from bs4 import BeautifulSoup
import random


# Global vars:
DEBUG = False # Set True for enabling debugging
soqurl = "http://stackoverflow.com/search?q="  # Query url
sourl = "http://stackoverflow.com"  # Site url
rn = -1  # Result number (for -r and --res)
ir = 0  # interactive mode off (for -i arg)
tag = "" # tag based search
data = dict() # Data file dictionary
data_file = os.path.join(os.path.dirname(__file__),"data.json") # Data file location
query = "" # Query
uas = [] # User agent list

### To support python 2:
if sys.version < '3.0.0':
    def urlencode(inp):
        return urllib.quote_plus(inp)
    def dispstr(inp):
        return inp.encode('utf-8')
    def inputs(str=""):
        sys.stdout.write(str)
        tempx = raw_input()
        return tempx
else:
    def urlencode(inp):
        return urllib.parse.quote_plus(inp)
    def dispstr(inp):
        return inp
    def inputs(str=""):
        sys.stdout.write(str)
        tempx = input()
        return tempx

### Fixes windows active page code errors
def fixCodePage():
    if sys.platform == 'win32':
        if sys.stdout.encoding != 'cp65001':
            os.system("echo off")
            os.system("chcp 65001") # Change active page code
            sys.stdout.write("\x1b[A") # Removes the output of chcp command
            sys.stdout.flush()
            return
        else:
            return


# Bold and underline are not supported by colorama.
class bcolors:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def format_str(str, color):
    return "{0}{1}{2}".format(color, str, colorama.Style.RESET_ALL)


def print_header(str):
    print(format_str(str, colorama.Fore.MAGENTA))


def print_blue(str):
    print(format_str(str, colorama.Fore.BLUE))


def print_green(str):
    print(format_str(str, colorama.Fore.GREEN))


def print_warning(str):
    print(format_str(str, colorama.Fore.YELLOW))


def print_fail(str):
    print(format_str(str, colorama.Fore.RED))


def print_white(str):
    print(format_str(str,colorama.Fore.WHITE))


def bold(str):
    return (format_str(str, bcolors.BOLD))


def underline(str):
    return (format_str(str, bcolors.UNDERLINE))

## For testing exceptions
def showerror(e):
    if DEBUG == True:
        import traceback
        print("Error name: "+ e.__doc__)
        print()
        print("Description: "+str(e))
        print()
        traceback.print_exc()
    else:
        return



def socli(query):
    """
    SOCLI Code
    :param query: Query to search on stackoverflow
    :return:
    """
    query = urlencode(query)
    try:
        search_res = requests.get(soqurl + query, verify=False)
        soup = BeautifulSoup(search_res.text, 'html.parser')
        try:
            res_url = sourl + (soup.find_all("div", class_="question-summary")[0].a.get('href'))
        except IndexError:
            print_warning("No results found...")
            sys.exit(0)
        dispres(res_url)
    except UnicodeEncodeError as e:
        showerror(e)
        print_warning("\n\nEncoding error: Use \"chcp 65001\" command before using socli...")
        sys.exit(0)
    except requests.exceptions.ConnectionError:
        print_fail("Please check your internet connectivity...")
    except Exception as e:
        showerror(e)
        sys.exit(0)


def helpman():
    """
    Displays help
    :return:
    """
    print_header("Stack Overflow command line client:")
    print_green("\n\n\tUsage: socli [ Arguments ] < Search Query >\n\n")
    print_header("\n[ Arguments ] (optional):\n")
    print(" " + bold("--help or -h") + " : Displays this help")
    print(" " + bold("--query or -q") +
          " : If any of the following commands are used then you " \
          "must specify search query after the query argument")
    print(" " + bold("--interactive or -i") + " : To search in stack overflow"
                                              " and display the matching results. You can chose and "
                                              "browse any of the result interactively")
    print(" " + bold("--res or -r") +
          " : To select and display a result manually and display "
          "its most voted answer. \n   eg:- socli --res 2 --query "
          "foo bar: Displays the second search result of the query"
          " \"foo bar\"'s most voted answer")
    print(" " + bold("--tag or -t") +
          " : To search a query by tag on stack overflow.  Visit http://stackoverflow.com/tags to see the "
          "list of all tags."
          "\n   eg:- socli --tag javascript,node.js --query "
          "foo bar: Displays the search result of the query"
          " \"foo bar\" in stack overflow's javascript and node.js tags.")
    print(" " + bold("--new or -n") +
          " : Opens the stack overflow new questions page in your default browser. You can create a "
          "new question using it.")
    print(" " + bold("--user or -u") +
          " : Displays information about the user provided as the next argument(optional). If no argument is provided"
          " it will ask the user to enter a default username. Now the user can run the command without the argument."
          "\n   eg:- socli -u: Prompts and saves your username. Now you can just run soci -u to see the stats \n      "
          "  socli -u 22656: Displays info about user ID 22656")
    print(" " + bold("--del or -d") +
          " : Deletes the configuration file generated by socli -u command.")
    print(" " + bold("--api or -a") +
          " : Sets a custom API key for socli")
    print_header("\n\n< Search Query >:")
    print("\n Query to search on Stack overflow")
    print("\nIf no commands are specified then socli will search the stack "
          "overflow and simply displays the first search result's "
          "most voted answer.")
    print("If a command is specified then it will work according to the "
          "command.")
    print_header("\n\nExamples:\n")
    print(bold("socli") + " for loop in python")
    print(bold("socli -iq") + " while loop in python")
    print("\n\n SoCLI is an open source project hosted on github. Don't forget to star it if you liked it. Use GitHub"
          " issues to report problems: "+ underline("http://github.com/gautamkrishnar/socli"))



def get_questions_for_query(query):
    """
    Fetch questions for a query. Returned question urls are relative to SO homepage.
    At most 10 questions are returned.
    :param query: User-entered query string
    :return: list of [ (question_text, question_description, question_url) ]
    """
    questions = []
    search_res = requests.get(soqurl + query, verify=False)
    soup = BeautifulSoup(search_res.text, 'html.parser')
    try:
        soup.find_all("div", class_="question-summary")[0]  # For explicitly raising exception
    except IndexError:
        print_warning("No results found...")
        sys.exit(0)
    tmp = (soup.find_all("div", class_="question-summary"))
    tmp1 = (soup.find_all("div", class_="excerpt"))
    i = 0
    while (i < len(tmp)):
        if i == 10: break  # limiting results
        question_text = ' '.join((tmp[i].a.get_text()).split())
        question_text = question_text.replace("Q: ","")
        question_desc = (tmp1[i].get_text()).replace("'\r\n", "")
        question_desc = ' '.join(question_desc.split())
        question_local_url = tmp[i].a.get("href")
        questions.append( (question_text, question_desc, question_local_url) )
        i = i + 1
    return questions

def get_question_stats_and_answer(url):
    """
    Fetch the content of a StackOverflow page for a particular question.
    :param url: full url of a StackOverflow question
    :return: tuple of ( question_title, question_desc, question_stats, answers )
    """
    res_page = requests.get(url, verify=False)
    soup = BeautifulSoup(res_page.text, 'html.parser')
    question_title, question_desc, question_stats = get_stats(soup)
    answers = [s.get_text() for s in soup.find_all("div", class_="post-text")][1:] # first post is question, discard it.
    return question_title, question_desc, question_stats, answers

def socli_interactive(query):
    """
    Interactive mode
    :return:
    """

    class UnicodeText(urwid.Text):
        """ encode all text to utf-8 """

        def __init__(self, text):
            # As we were encoding all text to utf-8 in output before with dispstr, do it automatically for all input
            text = UnicodeText.to_unicode(text)
            urwid.Text.__init__(self, text)

        @classmethod
        def to_unicode(cls, markup):
            """convert urwid text markup object to utf-8"""
            try:
                return dispstr(markup)
            except AttributeError:
                mapped = [ cls.to_unicode(i) for i in markup]
                if isinstance(markup, tuple):
                    return tuple(mapped)
                else:
                    return mapped

    class QuestionPage(urwid.WidgetWrap):
        """
        Main container for urwid interactive mode.
        """
        def __init__(self, data):
            """
            Construct the Question Page.
            :param data: tuple of  (answers, question_title, question_desc, question_stats, question_url)
            """
            answers, question_title, question_desc, question_stats, question_url = data
            self.url = question_url
            self.answer_text = AnswerText(answers)
            answer_frame = urwid.Frame(
                header= urwid.Pile( [
                    HEADER,
                    QuestionText(question_title, question_desc, question_stats),
                    urwid.Divider('-')
                ]),
                body=self.answer_text,
                footer= urwid.Pile([
                    QuestionURL(question_url),
                    UnicodeText(u'\u2191: next question, \u2193: previous question, o: open in browser, \u2190: back')
                ])
            )
            urwid.WidgetWrap.__init__(self, answer_frame)


        def keypress(self, size, key):
            if key in {'down', 'b', 'B'}:
                self.answer_text.prev_ans()
            elif key in {'up', 'n', 'N'}:
                self.answer_text.next_ans()
            elif key in {'o', 'O'}:
                import webbrowser
                HEADER.event('browser', "Opening in your browser..." )
                webbrowser.open(self.url)
            elif key == 'left':
                LOOP.widget = QUESTION_PAGE



    class Header(UnicodeText):
        """
        Header of the question page. Event messages are recorded here.
        """
        def __init__(self):
            self.current_event = None
            UnicodeText.__init__(self, '')

        def event(self, event, message):
            self.current_event = event
            self.set_text(message)

        def clear(self, event):
            if self.current_event == event:
                self.set_text('')



    class AnswerText(urwid.WidgetWrap):
        """Answers to the question.

        Long answers can be navigated up or down using the mouse.
        """

        def __init__(self, answers):
            urwid.WidgetWrap.__init__(self, UnicodeText(''))
            self._selectable = True # so that we receive keyboard input
            self.answers = answers
            self.index = 0
            self.set_answer()

        def set_answer(self):
            """
            We must use a box adapter to get the text to scroll when this widget is already in
            a Pile from the main question page. Scrolling is necessary for long answers which are longer
            than the length of the terminal.
            """
            self.content =  [  ('less-important', 'Answer: ') ] + self.answers[self.index].split("\n")
            self._w = ScrollableTextBox(self.content)

        def prev_ans(self):
            """go to previous answer."""
            self.index -= 1
            if self.index < 0:
                self.index = 0
                HEADER.event('answer-bounds', "No previous answers." )
            else:
                HEADER.clear('answer-bounds')
            self.set_answer()

        def next_ans(self):
            """go to next answer."""
            self.index += 1
            if self.index > len(self.answers) - 1:
                self.index = len(self.answers) - 1
                HEADER.event('answer-bounds', "No more answers.")
            else:
                HEADER.clear('answer-bounds')
            self.set_answer()

        def __len__(self):
            """ return number of rows in this widget """
            return len(self.content)

    class ScrollableTextBox(urwid.ListBox):
        """ Display input text, scrolling through when there is not enough room.

        Scrolling through text takes a little work to support on Urwid.
        """

        def __init__(self, content):
            """
            :param content: text string to be displayed
            """
            lines = [ UnicodeText(line) for line in content ]
            body = urwid.SimpleFocusListWalker(lines)
            urwid.ListBox.__init__(self, body)

        def mouse_event(self, size, event, button, col, row, focus):
            SCROLL_WHEEL_UP = 4
            SCROLL_WHEEL_DOWN = 5
            if button == SCROLL_WHEEL_DOWN:
                self.keypress(size, 'down')
            elif button == SCROLL_WHEEL_UP:
                self.keypress(size, 'up')
            else:
                return False
            return True





    class QuestionText(UnicodeText):
        """ Title, description, and stats of the question,"""

        def __init__(self, title, description, stats):
            text = [ "Question: ", ('title', title), description, ('metadata', stats)]
            UnicodeText.__init__(self, text)



    class QuestionURL(UnicodeText):
        """ url of the question """

        def __init__(self, url):
            text = [('heading', 'Question URL: '), url]
            UnicodeText.__init__(self, text)



    class SelectQuestionPage(urwid.WidgetWrap):

        def display_text(self, index, question):
            question_text, question_desc, _ = question
            text = [
                ("warning", u"{}. {}\n".format(index, question_text)),
                question_desc+"\n",
            ]
            return text


        def __init__(self, questions):
            self.questions = questions
            widgets = [ self.display_text(i,q) for i, q in enumerate(questions)]
            self.questions_box = ScrollableTextBox(widgets)
            header = UnicodeText(('less-important', 'Select a question below:\n'))
            footer = UnicodeText( "0-9: select a question, any other key: exit.")
            frame = urwid.Frame(header=header,
                                body=urwid.Filler(self.questions_box, height=('relative',100), valign='top'),
                                footer=footer)
            urwid.WidgetWrap.__init__(self, frame)

        # Override parent method
        def selectable(self):
            return True

        def keypress(self, size, key):
            if key in '012345679':
            # fetch answers and question info
                question_url = self.questions[int(key)][2]
                self.select_question(question_url)
            elif key in {'down', 'up'}:
                self.questions_box.keypress(size, key)
            else:
                raise urwid.ExitMainLoop()

        def select_question(self, url):
            url = sourl + url
            question_title, question_desc, question_stats, answers = get_question_stats_and_answer(url)

            if not answers:
                print_warning("\n\nAnswer:\n\t No answer found for this question...")
                sys.exit(0)

            questions = QuestionPage( (answers, question_title, question_desc, question_stats, url) )
            LOOP.widget = questions



    palette = [('answer', 'default', 'default'),
               ('title', 'light green, bold', 'default'),
               ('heading', 'light green, bold', 'default'),
               ('metadata', 'dark green', 'default'),
               ('less-important','dark gray', 'default'),
               ('warning', 'yellow', 'default')
               ]
    HEADER = Header()

    try:
        questions = get_questions_for_query(query)
        QUESTION_PAGE = SelectQuestionPage(questions)
        LOOP = urwid.MainLoop(QUESTION_PAGE, palette)
        LOOP.run()

    except UnicodeEncodeError:
        print_warning("\n\nEncoding error: Use \"chcp 65001\" command before using socli...")
        sys.exit(0)
    except requests.exceptions.ConnectionError:
        print_fail("Please check your internet connectivity...")
    except Exception as e:
        showerror(e)
        print("exiting...")
        sys.exit(0)


def socl_manusearch(query, rn):
    """
    Manual search by question index
    :param query:
    :param rn:
    :return:
    """
    query = urlencode(query)
    try:
        search_res = requests.get(soqurl + query, verify=False)
        soup = BeautifulSoup(search_res.text, 'html.parser')
        try:
            res_url = sourl + (soup.find_all("div", class_="question-summary")[rn - 1].a.get('href'))
        except IndexError:
            print_warning("No results found...")
            sys.exit(1)
        dispres(res_url)
    except UnicodeEncodeError:
        print_warning("Encoding error: Use \"chcp 65001\" command before "
                      "using socli...")
        sys.exit(0)
    except requests.exceptions.ConnectionError:
        print_fail("Please check your internet connectivity...")
    except Exception as e:
        showerror(e)
        sys.exit(0)


def userpage(userid):
    """
    Stackoverflow user profile browsing
    :param userid:
    :return:
    """
    global data
    import stackexchange
    try:
        if "api_key" not in data:
            data["api_key"] = None
        userprofile = stackexchange.Site(stackexchange.StackOverflow,app_key=data["api_key"]).user(userid)
        print(bold("\n User: " + userprofile.display_name.format()))
        print("\n\tReputations: " + userprofile.reputation.format())
        print_warning("\n\tBadges:")
        print("\t\t   Gold: " + str(userprofile.gold_badges))
        print("\t\t Silver: " + str(userprofile.silver_badges))
        print("\t\t Bronze: " + str(userprofile.bronze_badges))
        print("\t\t  Total: " + str(userprofile.badge_total))
        print_warning("\n\tStats:")
        total_questions = len(userprofile.questions.fetch())
        unaccepted_questions = len(userprofile.unaccepted_questions.fetch())
        accepted = total_questions - unaccepted_questions
        rate = accepted / float(total_questions) * 100
        print("\t\t Total Questions Asked: "+ str(len(userprofile.questions.fetch())))
        print('\t\t        Accept rate is: %.2f%%.' % rate)
        print('\nMost experienced on %s.' % userprofile.top_answer_tags.fetch()[0].tag_name)
        print('Most curious about %s.' % userprofile.top_question_tags.fetch()[0].tag_name)
    except urllib.error.URLError:
        print_fail("Please check your internet connectivity...")
        exit(1)
    except Exception as e:
        showerror(e)
        if  str(e) == "400 [bad_parameter]: `key` doesn't match a known application":
            print_warning("Wrong API key... Deleting the data file...")
            del_datafile()
            exit(1)
        elif  str(e) in ("not enough values to unpack (expected 1, got 0)" , "400 [bad_parameter]: ids"):
            global manual
            if manual == 1:
                print_warning("Wrong user ID specified...")
                helpman()
                exit(1)
            print_warning("Wrong user ID... Deleting the data file...")
            del_datafile()
            exit(1)

        # Reaches here when rate limit exceeds
        print_warning("Stackoverflow exception. This might be caused due to the rate limiting: http://stackapps.com/questions/3055/is-there-a-limit-of-api-requests")
        print("Use http://stackapps.com/apps/oauth/register to register a new API key.")
        set_api_key()
        exit(1)

def set_api_key():
    """
    Sets a custom API Key
    :return:
    """
    import_json()
    api_key = inputs("Type an API key to continue: ")
    if len(api_key) > 0:
        data["api_key"] = api_key
        save_datafile()
    print_warning("\nAPI Key saved...")


def save_datafile():
    """
    Saves the data dictionary to a file named data_file
    :return:
    """
    #import json => Json imported globally
    global data
    global data_file
    with open(data_file, "w") as dataf:
        json.dump(data, dataf)


def load_datafile():
    """
    Loads the data dictionary form a file named data_file
    :return:
    """
    #import json => Json imported globally
    global data
    global data_file
    with open(data_file) as dataf:
        data = json.load(dataf)


def del_datafile():
    """
    Deletes the data file
    :return:
    """
    global data_file
    try:
        os.remove(data_file)
    except FileNotFoundError:
        print_warning("File not created.... Use socli -u to create a new configuration file.")
        exit(0)


def import_json():
    """
    imports json
    fixes #33(https://github.com/gautamkrishnar/socli/issues/33)
    :return:
    """
    global json # Importing json globally
    global JSONDecodeError
    try:
        import simplejson as json
    except ImportError:
        import json
    try:
        JSONDecodeError = json.JSONDecodeError
    except AttributeError:
        JSONDecodeError = ValueError

def loadseragents():
    global uas
    uas = []
    with open(os.path.join(os.path.dirname(__file__),"user_agents.txt"), 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1-1])
    random.shuffle(uas)

def wrongsyn(query):
    """
    Exits if query value is empty
    :param query:
    :return:
    """
    if query == "":
        print_warning("Wrong syntax!...\n")
        helpman()
        sys.exit(1)
    else:
        return


def get_stats(soup):
    """
    Get Question stats
    :param soup:
    :return:
    """
    question_title = (soup.find_all("a",class_="question-hyperlink")[0].get_text())
    question_stats = (soup.find_all("span",class_="vote-count-post")[0].get_text())
    question_stats = "Votes " + question_stats + " | " + (((soup.find_all("div",\
                        class_="module question-stats")[0].get_text()).replace("\n", " ")).replace("     "," | "))
    question_desc = (soup.find_all("div", class_="post-text")[0])
    add_urls(question_desc)
    question_desc = question_desc.get_text()
    question_stats = ' '.join(question_stats.split())
    return question_title, question_desc, question_stats


def add_urls(tags):
    """
    Adds the URL to any hyperlinked text found in a question
    or answer.
    :param tags:
    """
    images = tags.find_all("a")

    for image in images:
        if hasattr(image, "href"):
            image.string = "{} [{}]".format(image.text, image['href'])


def hastags():
    """
    Gets the tags and adds them to query url
    :return:
    """
    global soqurl
    global tag
    for tags in tag.split(","):
        soqurl = soqurl + "[" + tags + "]" + "+"


def dispres(url):
    """
    Display result page
    :param url:
    :return:
    """
    res_page = requests.get(url + query, verify=False)
    soup = BeautifulSoup(res_page.text, 'html.parser')
    question_title, question_desc, question_stats = get_stats(soup)

    print_warning("\nQuestion: " + dispstr(question_title))
    print(dispstr(question_desc))
    print("\t" + underline(question_stats))
    try:
        answer = (soup.find_all("div", class_="post-text"))[1]
        add_urls(answer)
        answer = (soup.find_all("div", class_="post-text")[1].get_text())
        global tmpsoup
        tmpsoup = soup
        print_green("\n\nAnswer:\n")
        print("-------\n" + dispstr(answer) + "\n-------\n")
        print(bold("Question URL:"))
        print_blue(underline(url)+"\n")
        return
    except IndexError as e:
        print_warning("\n\nAnswer:\n\t No answer found for this question...")
        sys.exit(0)


def main():
    """
    Main Function
    :return:
    """

    global rn  # Result number (for -r arg)
    global ir  # interactive mode off (for -i arg)
    global tag # tag based search (for -t arg)
    global query # query variable
    colorama.init() # for colorama support in windows
    fixCodePage() # For fixing codepage errors in windows

    # IF there is no command line options or if it is help argument:
    if (len(sys.argv) == 1) or ((sys.argv[1] == "-h") or (sys.argv[1] == "--help")):
        helpman()
        sys.exit(0)
    else:
        try:
            options, rem = getopt.getopt(sys.argv[1:],"niudat:r:q:", [ "new" , "interactive" , "user" , "debug" , "api" ,"tag=" , "res=" ,"query=" ])
        except getopt.GetoptError:
            helpman()
            sys.exit(1)
        loadseragents() # Populates the user agents array
        # Gets the CL Args
        if 'options' in locals():
            for opt, arg in options:
                if opt in ("-d","--debug"):
                    global DEBUG
                    DEBUG = True
                if opt in ("-i", "--interactive"):
                    ir = 1  # interactive mode on
                if opt in ("-r", "--res"):
                    try:
                        rn = int(arg) # Result Number
                    except ValueError:
                        print_warning("Wrong syntax...!\n")
                        helpman()
                        sys.exit(1)
                if opt in ("-t", "--tag"):
                    if len(arg)==0:
                        print_warning("Wrong syntax...!\n")
                        helpman()
                        sys.exit(1)
                    tag = arg
                    hastags()
                if opt in ("-q", "--query"):
                    query = arg
                    if len(rem) > 0:
                        query = query + " " + " ".join(rem)
                if opt in ("-n", "--new"):
                    import webbrowser
                    print_warning("Opening stack overflow in your browser...")
                    webbrowser.open(sourl + "/questions/ask")
                    sys.exit(0)
                if opt in ("-a", "--api"):
                    set_api_key()
                    exit(0)
                if opt in ("-d", "--del"):
                    del_datafile()
                    print_warning("Data files deleted...")
                    exit(0)
                if opt in ("-u", "--user"):
                    # Stackoverflow user profile support
                    import_json()
                    user = 0
                    if len(rem)==1:
                        try:
                            user = int(rem[0])
                            global manual # Manual mode from command line
                            manual = 1
                        except ValueError:
                            print_warning("Wrong syntax. User ID must be an integer. Follow the instructions on this page "
                                          "to get your User ID: http://meta.stackexchange.com/a/111130\n")
                            helpman()
                            exit(1)
                    else:
                        global data_file
                        global data
                        try:
                            load_datafile()
                            if "user" in data:
                                user = data["user"]
                            else:
                                raise  FileNotFoundError # Manually raising to get value
                        except JSONDecodeError:
                            # This maybe some write failures
                            del_datafile()
                            print_warning("Error in parsing the data file, it will be now deleted. Please rerun the "
                                          "socli -u command.")
                            exit(1)
                        except FileNotFoundError:
                            print_warning("Default user not set...\n")
                            try:
                                # Code to execute when first time user runs socli -u
                                data['user'] = int(inputs("Enter your Stackoverflow User ID: "))
                                save_datafile()
                                user = data['user']
                                print_green("\nUserID saved...\n")
                            except ValueError:
                                print_warning("\nUser ID must be an integer.")
                                print("\nFollow the instructions on this page to get your User ID: http://meta.stackexchange.com/a/111130")
                                exit(1)
                    userpage(user)
                    exit(0)

        if tag != "":
            wrongsyn(query)
        if (rn == -1) and (ir == 0) and tag == "":
            if sys.argv[1] in ['-q', '--query']:
                socli(" ".join(sys.argv[2:]))
            else:
                socli(" ".join(sys.argv[1:]))
        elif (rn > 0):
            wrongsyn(query)
            socl_manusearch(query, rn)
            sys.exit(0)
        elif (rn == 0):
            print_warning("Count starts from 1. Use: \"socli -i 2 -q python for loop\" for the 2nd result for the query")
            sys.exit(0)
        elif (ir == 1):
            wrongsyn(query)
            socli_interactive(query)
            sys.exit(0)
        elif query != "":
            socli(query)
            sys.exit(0)
        else:
            print_warning("Wrong syntax...!\n")
            helpman()
            sys.exit(0)


if __name__ == '__main__':
    main()
