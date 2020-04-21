import os
import json

while True:
    try:
        filename = str(input("Enter the filename for the .csv: "))
        stream = open(filename, 'r').read()
        break
    except Exception:
        print("Couldn't open the file. Try again.")
# While the file is a CSV, it is easier to use a quote as the delimiter.
values = stream.split("\"")
# The portal is the second value in the file. Has a trailing whitespace that must be removed
portal = values[1].lstrip()
# The list of gateways is the fourth value. It is a comma seperated list.
gateways = values[3].split(',')
# Put the portal as the first item in the list so it will be the default.
replyurls = ["https://"+portal+":443/SAML20/SP/ACS"]
# Put the portal as the first item in the list so it will be the default.
identifiers = ["https://"+portal+":443/SAML20/SP"]
# This section adds the gateways to a list in the correct format.
for g in gateways:
    replyurls.append("https://"+g.lstrip()+":443/SAML20/SP/ACS")
    identifiers.append("https://"+g.lstrip()+":443/SAML20/SP")
# The update command needs the objectId of the application. Find it using its name.
while True:
    try:
        appname = str(input("Enter the name of the application: "))
        tempresult = os.popen('az ad app list --display-name "'+appname+'"').read()
        result = json.loads(tempresult)
        # Capture the objectId of the application for the update command later.
        objectId = result[0]["objectId"]
        # Capture the current list of gateways in the application.
        originalreplyUrls = result[0]["replyUrls"]
        originalidentifierUris = result[0]["identifierUris"]
        # The list command will return non-exact matches. This help identify which
        # application it found.
        print('Modifying the application '+result[0]["displayName"])
        break
    except Exception:
        print("Couldn't find a application with that name. Try again.")

# Remove gateways from the lists if they are already conifgured in the app.
newreplyUrls = list(set(replyurls) - set(originalreplyUrls))
newidentifierUris = list(set(identifiers) - set(originalidentifierUris))

replyCommand = ""
idCommand = ""

# Generate a list of the new gateways seperated by a space.
for url in newreplyUrls:
    replyCommand += url+" "

for uri in newidentifierUris:
    idCommand += uri+" "

# Add the new values to the RelyURLS and Identifiers lists.
if replyCommand != "":
    print("Updating the ReplyURLs...")
    print(os.popen('az ad app update --id ' + objectId + ' --add replyUrls ' + replyCommand).read())
else:
    print("No new ReplyUrls...")

if idCommand != "":
    print("Updating the Identifier-URIs")
    print(os.popen('az ad app update --id ' + objectId + ' --add identifierUris ' + idCommand).read())
else:
    print("No new IdentifierUris...")
