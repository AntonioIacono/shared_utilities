#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Slixmpp: The Slick XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of Slixmpp.

    See the file LICENSE for copying permission.
"""

import logging
from getpass import getpass
from argparse import ArgumentParser

import slixmpp


class SendMsgBot(slixmpp.ClientXMPP):

    """
    A simple Slixmpp bot that will echo messages it
    receives, along with a short thank you message.
    """

    def __init__(self, jid, password, recipient, message):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.recipient = recipient
        self.message = message
        self.add_event_handler("session_start", self.start)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        #self.add_event_handler("message", self.message)

    async def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        await self.get_roster()
        self.send_message(mto=self.recipient,mbody=self.message,mtype='chat')
        self.disconnect()

"""
    def presence(self, pres):

        Process incoming presence stanzas to capture a token.

        Arguments:
             pres -- The received presence stanza.


        #print(pres)
        # JID that must be saved:
        print("JID:")
        #if 'from' in pres['status']:
        token = str(pres['from'])
        filename = "my_token.txt"

        with open(filename, 'w') as file:
            file.write(token)


    def message(self, msg):

        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.

        #if msg['type'] in ('chat', 'normal'):
            #msg.reply("Thanks for sending\n%(body)s" % msg).send()
            #print(msg)
        #print(msg)
"""

if __name__ == '__main__':
    # Setup the command line arguments.
    parser = ArgumentParser(description=SendMsgBot.__doc__)

    # Output verbosity options.
    parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                        action="store_const", dest="loglevel",
                        const=logging.ERROR, default=logging.INFO)
    parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                        action="store_const", dest="loglevel",
                        const=logging.DEBUG, default=logging.INFO)

    # JID and password options.
    parser.add_argument("-j", "--jid", dest="jid",
                        help="JID to use")
    parser.add_argument("-p", "--password", dest="password",
                        help="password to use")
    parser.add_argument("-t","--to",dest="to",
                        help="JID to send the message to")
    parser.add_argument("-m","--message",dest="message",
                        help="message to send")

    args = parser.parse_args()

    # Setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    if args.jid is None:
        args.jid = "mcu@xmpp-server.sw1.multimedia.arpa"
    if args.password is None:
        args.password = "password"
    if args.to is None:
        args.to = "mcg@xmpp-server.sw1.multimedia.arpa"
    if args.message is None:
       args.message = "Ground_Notify_Message"

    # Setup the EchoBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = SendMsgBot(args.jid, args.password, args.to, args.message)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    #xmpp.connect(use_ssl=False, force_starttls=False,disable_starttls=True)
    xmpp.connect()
    xmpp.process(forever=False)