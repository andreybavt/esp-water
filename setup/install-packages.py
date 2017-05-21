import upip
print("Installing packages :")
for package in ['micropython-uasyncio','micropython-umqtt.simple']:
    print("     - "+package)
    upip.install(package,"/")
