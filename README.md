# DESCRIPTION OF THE SCRIPT'S OPERATING ALGORITHM
The script logs in to the site.
Goes to the desired page.
In this case, it is the "New Malden Quality Plan" page.

In a loop:
Based on the "Activities / Locations" column,
goes through the page from top to bottom to the specified cell of this column.

If it encounters buttons in this column, it clicks on them
and moves on if it has not reached the specified cell of the column.

If it encounters an inscription containing "plot" in this column,
it scrolls to the "QC4J Side-Rise Rain-Screen Firebreak AIM Rain Sc" column.

In this "QC4J Side-Rise Rain-Screen Firebreak AIM Rain Sc" column,
clicks on the cell with the inscription "In Progress".

A new tab opens - a form with fields.
In this new tab, it checks the value of the "Contractor’s Quality Assurance form reference number" field.
If it contains a dot "." instead of a number, then it sets the value "BMS01.G01".
Clicks on the "Update" button, saving the form.
Closes the form and returns to the main page.
And if the field contains a number, the script simply closes the tab.

Then continues to work in a loop.
Thus, moving to the specified cell along the path, performing the instructions described above.

The script finishes working when it reaches the specified cell of the "Activities / Locations" column.
