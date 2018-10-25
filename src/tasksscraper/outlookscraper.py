#!/usr/bin/env python

"""tasksscraper.outlook: ...."""

__author__ = "Daniel Engvall"
__email__ = "daniel@engvalls.eu"

import applescript

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
''')


def get_outlook_tasks():
    outlook_tasks = scpt.call('getTasks')
    return outlook_tasks
