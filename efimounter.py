#!/usr/bin/env python

import os
import sys

def testEnvironment():
    statuscode = os.system("diskutil > /dev/null 2>&1")
    if statuscode != 0:
        print("This program cannot run on your operating system!")
        exit(1)


def getDiskutil():
    os.system("diskutil list > .efimounter.tmp")
    pass


def getEFIList():
    efiList = [ ]
    currentDisk = ''
    partitions = [ ]
    inDisk = False
    with open('.efimounter.tmp', 'r') as file:
        for line in file.readlines():
            if (inDisk):
                if line == '\n':
                    isEFI = False
                    for partition in partitions:
                        if " EFI EFI " in partition:
                            isEFI = True

                    if isEFI:
                        partitions.insert(0,currentDisk)
                        efiList.append(partitions)

                    partitions = [ ]
                    currentDisk = ''
                    inDisk = False

                else:
                    partitions.append(line)

            elif (line[0] == '/'):
                inDisk = True
                currentDisk = line

        file.close()

    os.system("rm .efimounter.tmp > /dev/null 2>&1")
    if len(efiList) == 0:
        print("No EFI-Partition found!")
        exit(1)

    return efiList


def mounter(identifier):
    os.system("sudo diskutil mount " + identifier)


def showEFI(efiList):
    efiIdentifiers = [ ]
    counter = 0
    for disk in efiList:
        print("")
        for partition in disk:
            partition = partition[:-1]
            if " EFI EFI " in partition:
                efiIdentifiers.append('/dev/' + partition[-7:])
                sys.stdout.write("\033[0;32m")
                print(partition)
                sys.stdout.write("\033[0;0m")

            else:
                print(partition)

    print("")
    if len(efiIdentifiers) == 1:
        print("You have only one EFI-Partition,")
        print("do you want to mount this partition? (y/n)")
        while True:
            target = str(raw_input(">>> "))
            if target == 'y':
                mounter(efiIdentifiers[0])
                return 0

            elif target == 'n':
                exit(0)

            else:
                print("Invalid input!")

    print("There are " + str(len(efiList)) + " EFI-Partitions on your Computer. Which do you want to mount?")
    print("")
    counter = 0
    for identifier in efiIdentifiers:
        counter += 1
        print("Type \'" + str(counter) + "\' to mount " + identifier)

    while True:
        try:
            target = int(raw_input(">>> "))

        except ValueError:
            print("Invalid selection!")
            continue

        if target > 0 and target <= len(efiIdentifiers):
            break

        print("Invalid selection!")

    mounter(efiIdentifiers[target - 1])


def main():
    testEnvironment()
    os.chdir(os.getenv("HOME"))
    os.system("rm .efimounter.tmp > /dev/null 2>&1")
    getDiskutil()
    showEFI(getEFIList())
    exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit(1)
    except EOFError:
        exit(1)
