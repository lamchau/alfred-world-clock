from __future__ import annotations

import os

ROOT = "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources"


class Icon(str):
    """plain string subclass replacing the slow Enum version."""

    def __new__(cls, value: str) -> Icon:
        return str.__new__(cls, value)


# pre-joined icon paths as class attributes
Icon.AR_DOCUMENT = Icon(os.path.join(ROOT, "ARDocument.icns"))
Icon.ARvOBJECT = Icon(os.path.join(ROOT, "ARObject.icns"))
Icon.ACCOUNTS = Icon(os.path.join(ROOT, "Accounts.icns"))
Icon.ACTIONS = Icon(os.path.join(ROOT, "Actions.icns"))
Icon.AIRDROP = Icon(os.path.join(ROOT, "AirDrop.icns"))
Icon.ALERT_NOTE = Icon(os.path.join(ROOT, "AlertNoteIcon.icns"))
Icon.ALERT_STOP = Icon(os.path.join(ROOT, "AlertStopIcon.icns"))
Icon.ALL_MY_FILES = Icon(os.path.join(ROOT, "AllMyFiles.icns"))
Icon.APPLICATIONS_FOLDER = Icon(os.path.join(ROOT, "ApplicationsFolderIcon.icns"))
Icon.BACKWARD_ARROW = Icon(os.path.join(ROOT, "BackwardArrowIcon.icns"))
Icon.BONJOUR = Icon(os.path.join(ROOT, "Bonjour.icns"))
Icon.BOOKMARK = Icon(os.path.join(ROOT, "BookmarkIcon.icns"))
Icon.BURNABLE_FOLDER = Icon(os.path.join(ROOT, "BurnableFolderIcon.icns"))
Icon.BURNING = Icon(os.path.join(ROOT, "BurningIcon.icns"))
Icon.CLOCK = Icon(os.path.join(ROOT, "Clock.icns"))
Icon.CONNECT_TO = Icon(os.path.join(ROOT, "ConnectToIcon.icns"))
Icon.FINDER = Icon(os.path.join(ROOT, "FinderIcon.icns"))
Icon.FULL_TRASH = Icon(os.path.join(ROOT, "FullTrashIcon.icns"))
Icon.GENERAL = Icon(os.path.join(ROOT, "General.icns"))
Icon.GENERIC_APPLICATION = Icon(os.path.join(ROOT, "GenericApplicationIcon.icns"))
Icon.GENERIC_DOCUMENT = Icon(os.path.join(ROOT, "GenericDocumentIcon.icns"))
Icon.GENERIC_FOLDER = Icon(os.path.join(ROOT, "GenericFolderIcon.icns"))
Icon.GENERIC_NETWORK = Icon(os.path.join(ROOT, "GenericNetworkIcon.icns"))
Icon.GENERIC_QUESTIONMARK = Icon(os.path.join(ROOT, "GenericQuestionMarkIcon.icns"))
Icon.HELP = Icon(os.path.join(ROOT, "HelpIcon.icns"))
Icon.HOME_FOLDER = Icon(os.path.join(ROOT, "HomeFolderIcon.icns"))
Icon.LOCKED = Icon(os.path.join(ROOT, "LockedIcon.icns"))
Icon.NOTIFICATIONS = Icon(os.path.join(ROOT, "Notifications.icns"))
Icon.TRASH = Icon(os.path.join(ROOT, "TrashIcon.icns"))
Icon.UNLOCKED = Icon(os.path.join(ROOT, "UnlockedIcon.icns"))
Icon.USER = Icon(os.path.join(ROOT, "UserIcon.icns"))
