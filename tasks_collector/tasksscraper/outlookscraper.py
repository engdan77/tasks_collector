#!/usr/bin/env python

"""tasksscraper.outlook: ...."""

__author__ = "Daniel Engvall"
__email__ = "daniel@engvalls.eu"

import applescript
import osascript
from typing import List
import json
from loguru import logger


def get_outlook_tasks_legacy() -> List:
    """Get Outlook tasks

    Returns:
        List of tasks from Outlook

    """
    # noinspection PyPep8,PyPep8
    scpt = applescript.AppleScript('''
    on getTasks()
    tell application "Microsoft Outlook"
    	-- get the currently selected task or tasks
    	set selectedTasks to selection
    	set taskList to {}
    	repeat with theTask in selectedTasks
    		if class of theTask is task then
    			set theName to name of theTask
    			set theCategory to category of theTask
    			set theContent to plain text content of theTask
    			set thePriority to priority of theTask
    			set theFolder to folder of theTask
    			set theFolder to name of theFolder
    			set theModificationDate to modification date of theTask
    			set theStartDate to start date of theTask
    			set theDueDate to due date of theTask
    			set theCompleteDate to completed date of theTask

    			if theContent is missing value then
    				set theContent to ""
    			end if

    			set catList to {}
    			repeat with oneCat in theCategory
    				set theCategoryName to name of oneCat
    				set catList to catList & theCategoryName
    			end repeat
    			set end of taskList to {taskName:theName, taskCategories:catList, taskContent:theContent, taskPriority:thePriority, taskFolder:theFolder, modifiedDate:theModificationDate, startDate:theStartDate, due:theDueDate, completeDate:theCompleteDate}
    		end if
    	end repeat
    	taskList
    end tell
    end getTasks
    ''')  # nopep8
    outlook_tasks = scpt.call('getTasks')
    return outlook_tasks


def get_outlook_tasks() -> List:
    """Get Outlook tasks

    Returns:
        List of tasks from Outlook

    """
    # noinspection PyPep8,PyPep8
    c, o, e = osascript.run('''
    tell application "Microsoft Outlook"
        activate
        display dialog "Will now process all current outlook tasks selected"
        set result to ""
        set selectedTasks to selection
        repeat with theTask in selectedTasks
            set c to "{"
            if class of theTask is task then
                set c to c & "\\"taskName\\": \\"" & name of theTask & "\\""
                set theContent to plain text content of theTask
                if theContent is missing value then
                    set theContent to ""
                end if
                set c to c & ",\\"taskContent\\": \\"" & theContent & "\\""
                set c to c & ",\\"taskPriority\\": \\"" & priority of theTask & "\\""
                set theFolder to folder of theTask
                set c to c & ",\\"taskFolder\\": \\"" & name of theFolder & "\\""
                set c to c & ",\\"modifiedDate\\": \\"" & modification date of theTask & "\\""
                set c to c & ",\\"startDate\\": \\"" & start date of theTask & "\\""
                set c to c & ",\\"due\\": \\"" & due date of theTask & "\\""
                set c to c & ",\\"completeDate\\": \\"" & completed date of theTask & "\\""
                set c to c & ",\\"taskPriority\\": \\"" & priority of theTask & "\\""
                set c to c & ",\\"taskPriority\\": \\"" & priority of theTask & "\\""
                
                set theCategory to category of theTask
                set catList to "["
                repeat with oneCat in theCategory
                    set theCategoryName to name of oneCat
                    set catList to catList & ",\\"" & theCategoryName & "\\""
                end repeat
                set catList to catList & "]"
                set c to c & ",\\"taskCategories\\": " & catList
                set c to c & "},"
            end if
            set result to result & c
        end repeat
    end tell
    return result
    ''') # nopep8
    o = o.strip(',')
    o = f'[{o}]'
    logger.info(f'got following from Outlook tasks: {o}')
    if c == 0:
        result = json.loads(o)
        return result
    else:
        return None