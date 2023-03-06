# Commandline IT Inventory (Cireson) Manager 
Historical archive of an inventory manager I wrote while working in the IT
department in college.  This was one of the first things I wrote in Python and
as such there are quite a few things that I'm doing pretty inefficiently! 
I've decided to leave the old design patterns in to "see how far I've come".

Was written to operate in both python2 and python3 with the following syntax:

python cireson --getUser -name REDACTED-<PCN>

python cireson --setUser -name REDACTED-<PCN> -newName

python cireson --getDetails
				--setDetails -imaged -initials <initials to use>
                    (Customary in department to leave "last changed" initials
                    on computer details)
				--isComplete
				--getModel
				--getPCN
				--getName
				--verify //checks for common errors, missing fields, etc, and prints a list


Before writing this, all inventory management was done by manually logging in
to the inventory portal and comparing inventory values by hand with a
spreadsheet one of the techs would draft up - extremely error prone and
exhausting as the portal was very slow and clunky.