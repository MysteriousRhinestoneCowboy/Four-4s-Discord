from discord import *
from discord.ext import tasks
import math
import time


token = "Put your own bot's token in here"
client = Client()
developerID = "Put your own userID here"


class ChannelData:
    """The object that handles all of the channel data"""
    def __init__(self, myCh, operations="⊗|&><×÷-+^C", leftOp="~㏑√Ⓒ㏒Ⓢ↓", rightOp="!°", numbers=".1234567890", req={},
                 temporary=60, ordered=False):
        self.channel = myCh
        self.points = {}
        self.equations = {}
        self.required = req
        self.ordered = ordered
        if not self.ordered:
            self.required.sort()
        self.temp = temporary

        self.orderOperations = (leftOp + "{", rightOp, "^", "C×÷", "+-", "><", "&", "⊗", "|", operations)
        self.numbers = numbers
        self.operations = operations
        self.leftOp = leftOp
        self.rightOp = rightOp
        self.current = 1
        self.increment = 1
        if temporary is False:
            self.current = "not a number"
        self.notification = [None, 0]

    def isMath(self, content):
        """Returns a tuple, first part is a boolean describing whether the input is a valid mathematical expression.
        If the first part is True, the second part is a list of the numbers, operators, and parentheses in order.
        If the first part is False, the second part is a string describing the part that caused the False result
        The third part is a boolean that returns True if the operation satisfies the requirements of the channel"""
        myContent = self.cleanCalc(content)
        myContent = self.collapseRep(myContent, "!")
        tempContent = ""
        brackIndx = 0
        brackets = "{}"
        for char in myContent:
            if char == "R":
                tempContent += str(brackets[brackIndx])
                brackIndx ^= 1
            else:
                tempContent += char
        myContent = tempContent
        operations = self.operations
        leftOp = self.leftOp
        rightOp = self.rightOp
        numbers = self.numbers
        output = []
        number = ""
        decimal = -1
        prevType = "("
        parCount = 0
        brackCount = [0]
        digits = []
        specialRepeatedOperations = "!"

        #print(myContent)

        for char in myContent:
            #print(char, output)
            specialBracks = False
            if len(output) > 3:
                if output[-2] == "[" and output[-3][-1] in specialRepeatedOperations:
                    specialBracks = True

            if specialBracks:
                if char in "0123456789":
                    if prevType is "num":
                        number += char
                    elif prevType is "(":
                        number += char
                        prevType = "num"
                elif char == "]":
                    if parCount != brackCount.pop(-1):
                        return False, f'You opened a parentheses in a bracketed section and didn\'t close it'
                    number = int(number)
                    output.append(number)
                    number = ""
                    decimal = -1

                    output.append(")")
                    output.append(char)
                    prevType = "rop"

                elif char in "-.":
                    return False, "You can only have a positive integer in brackets"
                else:
                    return False, "You must have a positive integer in those brackets"


            elif char in numbers:
                if char != ".":
                    digits.append(char)
                if prevType is "num":
                    number += char
                    if decimal >= 0:
                        decimal += 1
                    if char == ".":
                        if decimal >= 0:
                            return False, f"You cannot have two decimals in a number"
                        else:
                            decimal = 0
                elif prevType is "op":
                    number += char
                    if decimal >= 0:
                        decimal += 1
                    if char == ".":
                        if decimal >= 0:
                            return False, f"You cannot have two decimals in a number"
                        else:
                            decimal = 0
                    prevType = "num"
                elif prevType is "lop":
                    number += char
                    if decimal >= 0:
                        decimal += 1
                    if char == ".":
                        if decimal >= 0:
                            return False, f"You cannot have two decimals in a number"
                        else:
                            decimal = 0
                    prevType = "num"
                elif prevType is "rop":
                    return False, f'You must have an operator or parenthesis after {output[-2]}{output[-1]}'
                elif prevType is "(":
                    number += char
                    if decimal >= 0:
                        decimal += 1
                    if char == ".":
                        if decimal >= 0:
                            return False, f"You cannot have two decimals in a number"
                        else:
                            decimal = 0
                    prevType = "num"
                elif prevType is ")":
                    if char == ".":
                        if decimal >= 0:
                            return False, f"You cannot have two decimals in a number"
                        else:
                            decimal = 0
                    else:
                        number = char
                    prevType = "num"
                    output.append("×")
                elif prevType == "{":
                    number += char
                    if decimal >= 0:
                        decimal += 1
                    if char == ".":
                        if decimal >= 0:
                            return False, f"You cannot have two decimals in a number"
                        else:
                            decimal = 0
                    prevType = "num"


            elif char in leftOp:
                if prevType is "num":
                    if number == ".":
                        return False, f'"{number}"" is not a proper number'
                    number = self.makeInt(float(number))
                    output.append(number)
                    number = ""
                    decimal = -1

                    output.append("×")
                    output.append(" " + char)
                    prevType = "lop"
                elif prevType is "op":
                    output.append(" " + char)
                    prevType = "lop"
                elif prevType is "lop":
                    output.append(" " + char)
                    prevType = "lop"
                elif prevType is "rop":
                    return False, f'You cannot follow a right operator with a left operator as {output[-1]}{char}'
                elif prevType is "(":
                    output.append(" " + char)
                    prevType = "lop"
                elif prevType is ")":
                    output.append("×")
                    output.append(" " + char)
                    prevType = "lop"
                elif prevType is "{":
                    return False, "Only digits can be repeated"

            elif char in rightOp:
                if prevType is "num":
                    if number == ".":
                        return False, f'"{number}"" is not a proper number'
                    number = self.makeInt(float(number))
                    output.append(number)
                    number = ""
                    decimal = -1

                    output.append(" " + char)
                    prevType = "rop"
                elif prevType is "op":
                    return False, f'You cannot have a right operator following an operator as in {output[-1]}{char}'
                elif prevType is "lop":
                    return False, f'You cannot have a right operator following a left operator as in {output[-1]}{char}'
                elif prevType is "rop":
                    output.append(" " + char)
                elif prevType is "(":
                    return False, f'You cannot open a parenthesized section with a right operator ({char})'
                elif prevType is ")":
                    output.append(" " + char)
                    prevType = "rop"
                elif prevType is "{":
                    return False, "Only digits can be repeated"

            elif char in operations:
                if prevType is "num":
                    if number == ".":
                        return False, f'"{number}"" is not a proper number'
                    number = self.makeInt(float(number))
                    output.append(number)
                    number = ""
                    decimal = -1

                    output.append(" " + char)
                    prevType = "op"
                elif prevType is "op":
                    if char == "-":
                        output.append("↓")
                        prevType = "lop"
                    else:
                        return False, f"You cannot have two operations in a row like this: {output[-1]} {char}!"
                elif prevType is "lop":
                    if char == "-":
                        output.append("↓")
                        prevType = "lop"
                    else:
                        return False, f'You must have a number after {output[-1]}'
                elif prevType is "rop":
                    output.append(" " + char)
                    prevType = "op"
                elif prevType is "(":
                    if char == "-":
                        output.append("↓")
                        prevType = "lop"
                    else:
                        return False, f"You cannot start a parenthesized section with a {char}!"
                elif prevType is ")":
                    output.append(" " + char)
                    prevType = "op"
                elif prevType is "{":
                    return False, "Only digits can be repeated"

            elif char is "(":
                parCount += 1
                if prevType is "num":
                    if number == ".":
                        return False, f'"{number}"" is not a proper number'
                    number = self.makeInt(float(number))
                    output.append(number)
                    number = ""
                    decimal = -1

                    output.append("×")
                    output.append(char)
                    prevType = char
                elif prevType is "op":
                    output.append(char)
                    prevType = char
                elif prevType is "lop":
                    output.append(char)
                    prevType = char
                elif prevType is "rop":
                    output.append("×")
                    output.append(char)
                    prevType = char
                elif prevType is "(":
                    output.append(char)
                elif prevType is ")":
                    output.append("×")
                    output.append(char)
                    prevType = char
                elif prevType is "{":
                    return False, "Only digits can be repeated"

            elif char is ")":
                parCount -= 1
                if parCount < brackCount[-1]:
                    return False, f'You cannot close a parentheses you never opened'

                if prevType is "num":
                    if number == ".":
                        return False, f'"{number}"" is not a proper number'
                    number = self.makeInt(float(number))
                    output.append(number)
                    number = ""
                    decimal = -1

                    output.append(char)
                    prevType = char
                elif prevType is "op":
                    return False, f'You cannot close a parentheses after an operator like {output[-1]}'
                elif prevType is "lop":
                    return False, f'You must follow a left operator like {output[-1]} with ' \
                        f'a number or an opening parenthesis/bracket'
                elif prevType is "rop":
                    output.append(char)
                    prevType = char
                elif prevType is "(":
                    return False, f'You cannot have an empty set of parentheses'
                elif prevType is ")":
                    output.append(char)
                elif prevType is "{":
                    return False, "Only digits can be repeated"

            elif char is "[":
                brackCount.append(parCount)
                if prevType is "num":
                    return False, f'Brackets can only be used to modify operators, not after a number'
                elif prevType is "op":
                    output.append(char)
                    output.append("(")
                    prevType = "("
                elif prevType is "lop":
                    output.append(char)
                    output.append("(")
                    prevType = "("
                elif prevType is "rop":
                    output.append(char)
                    output.append("(")
                    prevType = "("
                elif prevType is "(":
                    return False, f'Brackets can only be used to modify operators, not after a parenthesis'
                elif prevType is ")":
                    return False, f'Brackets can only be used to modify operators, not after a parenthesis'
                elif prevType is "{":
                    return False, "Only digits can be repeated"

            elif char is "]":
                if parCount != brackCount.pop(-1):
                    return False, f'You opened a parentheses in a bracketed section and didn\'t close it'

                if prevType is "num":
                    if number == ".":
                        return False, f'"{number}"" is not a proper number'
                    number = self.makeInt(float(number))
                    output.append(number)
                    number = ""
                    decimal = -1

                    if output[-4][-1] == "!":
                        for i in str(output[-1]):
                            digits[i] -= 1
                        prevType = "rop"
                    else:
                        prevType = "op"
                    output.append(")")
                    output.append(char)
                elif prevType is "op":
                    return False, f'You cannot end a bracketed section after an operator like {output[-1]}'
                elif prevType is "lop":
                    return False, f'A left operator ({output[-1]}) must be followed by a number, not a bracket'
                elif prevType is "rop":
                    output.append(")")
                    output.append(char)
                    prevType = "op"
                elif prevType is "(":
                    return False, "You cannot end a bracketed section with an opening parenthesis"
                elif prevType is ")":
                    output.append(")")
                    output.append(char)
                    prevType = "op"
                elif prevType is "{":
                    return False, "Only digits can be repeated"

            elif char == "{":
                if prevType is "num":
                    if decimal == -1:
                        return False, "You cannot repeat digits before the decimal"
                    else:
                        if number == "." or number == "":
                            number = 0
                        brackIndx = decimal
                    number = self.makeInt(float(number))
                    output.append(number)
                    number = ""
                    decimal = -1
                    output.append(f'{brackIndx} {char}')
                    prevType = "{"
                else:
                    return False, "You can only repeat digits after a decimal"

            elif char == "}":
                if prevType == "num":
                    if decimal == -1:
                        if isinstance(output[-1], str):
                            if output[-1][-1] == "{":
                                brackIndx = len(number)
                                output.append(number)
                                number = ""

                                output.append(f'{brackIndx} {char}')
                                prevType = "rop"
                            else:
                                return False, "A repeated section must only include digits"
                        else:
                            return False, f'You must only repeat digits after the decimal point'
                    else:
                        return False, "A decimal point cannot be repeated"
                else:
                    return False, "Only digits can be repeated"


            elif char == "=":
                break

            else:
                if char in "0123456789":
                    return False, f'You cannot use the numeral {char}'
                else:
                    return False, f'{char} is not a valid character for a mathematical expression'

        if parCount != 0:
            return False, "You have an unclosed parentheses"

        elif prevType is "num":
            if number == ".":
                return False, f'"{number}"" is not a proper number'
            number = self.makeInt(float(number))
            output.append(number)

        elif prevType in ("lop", "op", "("):
            return False, f"You cannot end the mathematical statement with {output[-1]}"

        #print(output, digits)
        return True, output, digits

    def makeInt(self, x):
        """Converts a float to int if the float is equal to an integer"""
        try:
            if int(x) == x:
                return int(x)
            else:
                return x
        except TypeError:
            return x

    def cleanCalc(self, content):
        """Cleans up text for the calc function, mostly replacing operators with single characters"""
        output = content.lower()
        output = output.replace("sqrt", "√")
        output = output.replace("rt", "√")
        output = output.replace("log", "㏒")
        output = output.replace("ln", "㏑")
        output = output.replace("and", "&")
        output = output.replace("xor", "⊗")
        output = output.replace("or", "|")
        output = output.replace("<<", "<")
        output = output.replace(">>", ">")
        output = output.replace("cos", "Ⓒ")
        output = output.replace("sin", "Ⓢ")
        output = output.replace("pi", "π")
        output = output.replace("phi", "ɸ")
        output = output.replace("c", "C")
        output = output.replace("!", "!")
        output = output.replace("**", "^")
        output = output.replace("—", "--")
        output = output.replace("minus", "-")
        output = output.replace("plus", "+")
        output = output.replace("over", "÷")
        output = output.replace("/", "÷")
        output = output.replace("times", "×")
        output = output.replace("x", "×")
        output = output.replace("*", "×")
        output = output.replace(" ", "")
        output = output.replace("__", "R")
        return output

    def calculate(self, content):
        """Calculates the whole expression. This is the main method that gets called by players"""
        myContent = content[: ]
        while "(" in myContent:
            parentheses = self.getParentheses(myContent)
            inside = self.solve(myContent[parentheses[0] + 1: parentheses[1]])
            if isinstance(inside, tuple):
                return inside

            myContent = myContent[: parentheses[0]] + inside + myContent[parentheses[1] + 1: ]
            if myContent[parentheses[0] - 1] == "[":
                myContent = myContent[: parentheses[0] - 2] + \
                            [f'{myContent[parentheses[0]]} {myContent[parentheses[0] - 2]}'] + \
                            myContent[parentheses[0] + 2: ]
        result = self.solve(myContent)
        return result

    def getParentheses(self, content):
        """Returns a tuple representing the indices of the first closing parenthesis and its corresponding opening"""
        first = 0
        for i in range(len(content)):
            if content[i] == "(":
                first = i
            elif content[i] == ")":
                return first, i

    def collapseRep(self, content, operation):
        """Checks to see if the given operation is repeated multiple times and collapses it
        into a single operator with the number of repetitions in brackets.
        Currently only used for multifactorials, could theoretically be used for up-arrow notation"""
        output = content
        while operation * 2 in output:
            i = 3
            while operation * i in output:
                i += 1
            i -= 1
            output = output.replace(operation * i, f'{operation}[{i}]')
        return output

    def solve(self, content):
        """Solves a mathematical expression if it doesn't have parentheses in it, called by calculate"""
        myContent = content[: ]
        while len(myContent) > 1:
            indx = (0, 10)
            for i in range(len(myContent)):
                if isinstance(myContent[i], str):
                    for tier in range(len(self.orderOperations)):
                        if myContent[i][-1] in self.orderOperations[tier]:
                            if tier < indx[1]:
                                indx = (i, max(tier, 1))
            indx = indx[0]
            myOp = myContent[indx][-1]
            baseStr = myContent[indx].split(" ")[0]

            indx0 = -1
            indx1 = 2

            if myOp in self.leftOp:
                indx0 += 1
            elif myOp in self.rightOp:
                indx1 -= 1
            else:
                pass

            if myOp == "{":
                indx1 += 1
                myY = myContent[indx - 1] + int(myContent[indx + 1]) / \
                      int(
                          "9" * int(myContent[indx + 2][: -2]) +
                          "0" * int(myContent[indx][: -2]))
            elif myOp == "!":
                if baseStr == "":
                    base = 1
                else:
                    base = int(baseStr)
                if base < 1:
                    return False, "Don't mess around too much with the multifactorials, kids"
                elif not isinstance(myContent[indx - 1], int):
                    return False, "Only integer factorials allowed here"
                elif myContent[indx - 1] < 0:
                    return False, "No negative factorials"
                elif myContent[indx - 1] >= 1024:
                    return False, "That's too big!"
                myY = 1
                i = myContent[indx - 1]
                while i > 1:
                    myY *= i
                    i -= base
            elif myOp == "°":
                myY = myContent[indx - 1] * math.pi / 180
            elif myOp == "~":
                if not isinstance(myContent[indx + 1], int):
                    return False, "You can only perform bitwise NOT operations on integers"
                elif myContent[indx + 1] < 0:
                    myX = -1 * myContent[indx + 1]
                else:
                    myX = myContent[indx + 1]
                i = 1
                while i <= myX:
                    i *= 2
                myY = (i - myX - 1) * (myX // myContent[indx + 1])
            elif myOp == "↓":
                myY = -1 * myContent[indx + 1]
            elif myOp == "Ⓒ":
                myY = math.cos(myContent[indx + 1])
            elif myOp == "Ⓢ":
                myY = math.sin(myContent[indx + 1])
            elif myOp == "㏒":
                if myContent[indx + 1] < 0:
                    return False, "No imaginary numbers"
                elif myContent[indx + 1] == 0:
                    return False, "You cannot take the log of 0"
                base = myContent[indx].split(" ")[0]
                if base == "":
                    base = 2
                else:
                    base = float(base)
                if base < 0:
                    return False, "No imaginaries!"
                elif base == 0:
                    return False, "The base cannot be 0"
                elif base == 1:
                    return False, "the base cannot be 1"
                elif base == 2:
                    myY = math.log2(myContent[indx + 1])
                elif base == 10:
                    myY = math.log10(myContent[indx + 1])
                else:
                    myY = math.log(myContent[indx + 1], base)
            elif myOp == "㏑":
                if myContent[indx + 1] < 0:
                    return False, "I said no imaginary numbers"
                elif myContent[indx + 1] == 0:
                    return False, "You cannot take ln of 0"
                myY = math.log(myContent[indx + 1])
            elif myOp == "√":
                if myContent[indx + 1] < 0:
                    return False, "Let's just ignore imaginary numbers"
                base = myContent[indx].split(" ")[0]
                if base == "":
                    base = 2
                else:
                    base = int(base)
                myY = myContent[indx + 1] ** (1 / base)
            elif myOp == "C":
                n = myContent[indx - 1]
                k = min(n - myContent[indx + 1], myContent[indx + 1])
                if not isinstance(k, int) or not isinstance(n, int):
                    return False, "Both arguments must be integers"
                elif n < 0 or myContent[indx + 1] < 0:
                    return False, "Both arguments mst be nonnegative"
                elif k < 0:
                    myY = 0
                else:
                    myY = 1
                    for i in range(k):
                        myY *= n
                        myY /= i + 1
                        n -= 1
            elif myOp == "^":
                if myContent[indx + 1] > 4096 and myContent[indx - 1] > 1:
                    return False, "Please, let's not get too carried away here"
                elif myContent[indx + 1] < 1 and myContent[indx - 1] < 0:
                    return False, "Let's just ignore imaginary numbers"
                myY = myContent[indx - 1] ** myContent[indx + 1]
            elif myOp == "×":
                myY = myContent[indx - 1] * myContent[indx + 1]
            elif myOp == "÷":
                if myContent[indx + 1] == 0:
                    return False, "You cannot divide by zero"
                myY = myContent[indx - 1] / myContent[indx + 1]
            elif myOp == "+":
                myY = myContent[indx - 1] + myContent[indx + 1]
            elif myOp == "-":
                myY = myContent[indx - 1] - myContent[indx + 1]
            elif myOp == ">":
                if isinstance(myContent[indx - 1], int) and isinstance(myContent[indx + 1], int):
                    myY = myContent[indx - 1] >> myContent[indx + 1]
                else:
                    return False, "You can only use integers for right shift"
            elif myOp == "<":
                if isinstance(myContent[indx - 1], int) and isinstance(myContent[indx + 1], int):
                    myY = myContent[indx - 1] << myContent[indx + 1]
                else:
                    return False, "You can only use integers for left shift"
            elif myOp == "&":
                if isinstance(myContent[indx - 1], int) and isinstance(myContent[indx + 1], int):
                    myY = myContent[indx - 1] & myContent[indx + 1]
                else:
                    return False, "You can only use integers for bitwise AND operations"
            elif myOp == "⊗":
                if isinstance(myContent[indx - 1], int) and isinstance(myContent[indx + 1], int):
                    myY = myContent[indx - 1] ^ myContent[indx + 1]
                else:
                    return False, "You can only use integers for bitwise XOR operations"
            elif myOp == "|":
                if isinstance(myContent[indx - 1], int) and isinstance(myContent[indx + 1], int):
                    myY = myContent[indx - 1] | myContent[indx + 1]
                else:
                    return False, "You can only use integers for bitwise OR operations"

            myY = self.makeInt(myY)
            myContent = myContent[: indx + indx0] + [myY] + myContent[indx + indx1:]
        return myContent

    def expressString(self, content):
        """Creates a cleaned up string of the mathematical expression"""
        myContent = self.cleanCalc(content).split("=")[0]
        myContent = myContent.replace("Ⓢ", "sin")
        myContent = myContent.replace("Ⓒ", "cos")
        myContent = myContent.replace("=", "")
        spacedOperations = "+-÷×⊗|&><"
        for operation in spacedOperations:
            myContent = myContent.replace(operation, f' {operation} ')
        myContent = myContent.replace(">>", ">")
        myContent = myContent.replace(">", ">>")
        myContent = myContent.replace("<<", "<")
        myContent = myContent.replace("<", "<<")
        myContent = myContent.replace("R", "__")
        return myContent

    def meetsMin(self, ismath):
        """Returns True if the content has the correct number of the numerals specified in required, False otherwise"""
        if self.temp is False:
            return True
        if self.ordered is False:
            ismath.sort()
        if ismath == self.required:
            return True
        else:
            output = []
            for digit in "1234567890":
                if ismath.count(digit) != self.required.count(digit):
                    output.append(digit)
            if output is []:
                return False
            else:
                return output

    def givePoints(self, userID, points):
        """Increases a user's points by the given number points"""
        myPoints = self.points.get(userID, 0) + points
        self.points[userID] = myPoints

    def awardCheck(self, message, result):
        """Gives a reward if result is equal to self.current. Does nothing otherwise other than return False"""
        if result == self.current:
            self.givePoints(message.author.id, self.current)
            self.current += 1
            return True
        else:
            return False

    async def updateNotice(self):
        """Gets called every minute, updates the notification if notification[1] has reached 120 (2 hours),
        posts a new notification if the target has gone up"""
        expired = False
        if isinstance(self.current, int) is False:
            return False
        elif self.notification[0] is None:
            newMess = await self.channel.send(f'The target number is **{self.current}**.\nThis will be updated at ' \
                                              f'{(int(time.strftime("%H")) + self.increment) % 24}:{time.strftime("%M")} '
                                              f'if no correct answer is submitted')
            self.notification = [newMess, 0]
        else:
            self.notification[1] += 1
            myTime = self.notification[1]
            target = int(self.notification[0].content.split("**")[1])

            if myTime >= 60 * self.increment:
                self.current += 1
                self.increment = min(self.increment + 1, 24)
                self.notification[1] = 0
                expired = True

            if target < self.current:
                if not expired:
                    self.increment = 1
                newContent = f'The target number is **{self.current}**.\nThis will be updated at ' \
                    f'{(int(time.strftime("%H")) + self.increment) % 24}:{time.strftime("%M")} ' \
                    f'{["", "tomorrow "][self.increment // 24]}' \
                    f'if no correct answer is submitted before then.'
                try:
                    lastMessage = await self.channel.fetch_message(self.channel.last_message_id)
                except NotFound:
                    lastMessage = None

                if self.notification[0] == lastMessage:
                    await self.notification[0].edit(content=newContent)
                elif lastMessage is None:
                    newMessage = await self.channel.send(newContent)
                    self.notification[0] = newMessage
                else:
                    await self.notification[0].delete()
                    newMessage = await self.channel.send(newContent)
                    self.notification[0] = newMessage


myChannels = {}


@tasks.loop(minutes=1)
async def updateChannels():
    for key in myChannels:
        if key != "start":
            _channel = myChannels[key]
            try:
                await _channel.updateNotice()
            except Exception as inst:
                print(f'There\'s an error in updateNotice that\'s not tryed: {inst}, {type(inst)}')


@updateChannels.after_loop
async def after_my_loop():
    print(f'The loop has finished at {time.strftime("%H:%M:%S:, %b %d", time.localtime())}')


@client.event
async def on_ready():
    if myChannels.get("start", False):
        print(f'on_ready at {time.strftime("%H:%M:%S, %b %d", time.localtime())}')
    else:
        readyMessage = "Reporting for duty in:"
        for _guild in client.guilds:
            for _channel in _guild.text_channels:
                temporary = 60
                ordered = False
                req = []
                numbers = "."
                for digit in _channel.name:
                    if digit in "1234567890":
                        req.append(digit)
                        if digit not in numbers:
                            numbers += digit
                if numbers == ".":
                    numbers = ".0123456789"
                if "general" in _channel.name:
                    temporary = False
                if "ordered" in _channel.name:
                    ordered = True
                myChannels[_channel.id] = ChannelData(_channel, numbers=numbers, req=req,
                                                      temporary=temporary, ordered=ordered)
                readyMessage += f' {_channel.name}({_channel.id}),'
        updateChannels.start()
        myChannels["start"] = True
        readyMessage = readyMessage[: - 1] + f'\nStarting at {time.strftime("%H:%M:%S, %b %d", time.localtime())}'
        print(readyMessage)


@client.event
async def on_guild_channel_create(channel):
    temporary = 60
    ordered = False
    req = []
    numbers = "."
    for digit in channel.name:
        if digit in "1234567890":
            req.append(digit)
            if digit not in numbers:
                numbers += digit
    if numbers == ".":
        numbers = ".0123456789"
    if "general" in channel.name:
        temporary = False
    if "ordered" in channel.name:
        ordered = True
    myChannels[channel.id] = ChannelData(channel, numbers=numbers, req=req, temporary=temporary, ordered=ordered)
    print(f'{channel.name} created at {time.strftime("%H:%M:%S, %b %d")} with id {channel.id}')


@client.event
async def on_message(message):
    commandFlag = "/"
    words = message.content.lower().split(" ")
    command = words[0][len(commandFlag): ]
    try:
        myChannel = myChannels[message.channel.id]
        temporary = myChannel.temp
    except KeyError:
        print(f"I think {message.channel} is a private channel")
        return False

    if message.author.bot is True:
        return False

    elif len(message.content) >= len(commandFlag):
        if message.content[: len(commandFlag)] == commandFlag:

            if command == "print":
                print(message.content[len(commandFlag + command): ])
                await message.delete()

            elif command == "purge":
                if message.author.id != developerID:
                    return False
                await message.channel.purge()

            elif command == "loop":
                if message.author.id != developerID:
                    return False
                updateChannels.restart()

            elif command in ("score", "scores", "points"):
                if myChannel.temp is False:
                    return False
                scores = []
                response = "The scores are:\n" + "**" + ("~ " * 15) + "**"
                for guildMember in message.guild.members:
                    scoreIndx = (myChannel.points.get(guildMember.id, 0), guildMember.display_name)
                    if guildMember.bot is False:
                        scores.append(scoreIndx)
                scores.sort()
                scores.reverse()
                for guildMember in scores:
                    response += f'\n{guildMember[1]}: **{guildMember[0]}**'
                await respond(message, response, delay=max(1, temporary * 5))

            elif command in ("target", "current"):
                await myChannel.updateNotice()
                """if isinstance(myChannel.current, int):
                    await respond(message, f'Your current target is {myChannel.current}', delay=temporary)
                else:
                    await respond(message, "This channel does not have a target number", delay=max(temporary // 10, 10))"""

        else:
            mathCheck = myChannel.isMath(message.content)
            if mathCheck[0]:
                if myChannel.meetsMin(mathCheck[2]) is True:
                    response = f'{myChannel.expressString(message.content)}=\n**'
                    result = myChannel.calculate(mathCheck[1])
                    if result[0] is False:
                        response = result[1]
                    else:
                        response += f'{result[0]}**'
                    if myChannel.awardCheck(message, result[0]):
                        temporary = False
                        await message.add_reaction("✅")
                    await respond(message, response, 2000, delay=temporary)
                elif myChannel.meetsMin(mathCheck[2]) is False:
                    response = "The digits need to be entered in the order:"
                    for char in myChannel.required:
                        response += f' {char},'
                    response = response[: -1]
                    await respond(message, response, delay=max(1, temporary // 10))
                else:
                    response = "There needs to be exactly:"
                    numKeys = {1: "ones", 2: "twos", 3: "threes", 4: "fours", 5: "fives",
                               6: "sixes", 7: "sevens", 8: "eights", 9: "nines", 0: "zeroes"}
                    for key in myChannel.meetsMin(mathCheck[2]):
                        response += f' {myChannel.required.count(key)} {numKeys[int(key)]},'
                    response = response[: -1] + " in the expression"
                    if myChannel.temp is False:
                        return False
                    else:
                        await respond(message, response, delay=max(1, temporary // 10))

            else:
                if myChannel.temp is False:
                    return False
                else:
                    await respond(message, mathCheck[1], delay=max(1, temporary // 10))

    if temporary:
        await message.delete(delay=temporary)


async def respond(message, response, maxLen=10000, delay=False):
    """Sends the response to the comment.channel.
    If the response is longer than 2000 characters it breaks the response up to meet comment length limits.
    If the response is longer than the maxLen the response won't send"""
    if len(response) > maxLen:
        return False
    commentLength = 2000
    for i in range(len(response) // commentLength + 1):
        commentStart = i * commentLength
        myCom = await message.channel.send(response[commentStart: min(commentStart + commentLength, len(response))])
        if delay:
            await myCom.delete(delay=delay)


client.run(token)
