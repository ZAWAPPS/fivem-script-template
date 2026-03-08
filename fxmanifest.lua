fx_version 'cerulean'
lua54 'yes'
game 'gta5'

name 'SCRIPT_NAME'
description 'SCRIPT_DESCRIPTION'
version '1.0.0'
author 'ZAWAPPS'

shared_scripts {
    'shared/*.lua'
}

-- Encrypted file handling (Uncomment to exclude files from escrow)
escrow_ignore {
    'shared/config.lua'
}

ui_page 'web/dist/index.html'

client_scripts {
    'client/*.lua'
}

server_scripts {
    'server/*.lua'
}