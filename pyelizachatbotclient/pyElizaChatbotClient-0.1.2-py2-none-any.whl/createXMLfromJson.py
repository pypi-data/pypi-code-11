import os
import codecs
import sys
import traceback

# External packages
try:
    from nltk import word_tokenize
except ImportError:
    try:
        import nltk
        nltk.download('punkt')
    except:
        raise ImportError('This program cannot run without NLTK and its tokenizer module.'
                          'use: pip install nltk')
    else:
        from nltk import word_tokenize

try:
    import petl as etl
except ImportError:
    raise ImportError('This program cannot run without petl module. Use pip to install it')

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from xml.dom import minidom



def prettify(elem):
    """Return a pretty-printed XML string for the Element"""
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def process_text(txt, chatbot_name=None, user_name=None):
    # Remove whitespaces
    txt = ' '.join(txt.split())
    if chatbot_name is not None or user_name is not None:
        words = word_tokenize(txt)
        if chatbot_name is not None:
            for pos in [i for i, x in enumerate(words) if x.lower() == chatbot_name.lower()]:
                words[pos] = 'SYSTEM_NAME'

        if user_name is not None:
            for pos in [i for i,x in enumerate(words) if x.lower() == user_name.lower()]:
                words[pos] = 'USER_NAME'

        txt = ' '.join(words)
    return txt


def fntCreateXMLFromLogs(name_chatbot='Eliza', name_user='John', name_logfile='pyEliza.log'):

    out_xml_file = os.path.splitext(os.path.abspath(name_logfile))[0]+".xml"
    print('Creating XML (%s) from Log file (%s)' %(out_xml_file, name_logfile))

    try:
        if name_logfile is None: name_logfile = 'pyEliza.log'
        if name_chatbot is None: name_chatbot = 'Eliza'
        if name_user is None: name_user = 'UNKNOWN'

        dialogues_xml = Element("dialogues")
        header_row = ['date', 'module', 'level', 'type_msg', 'msg']
        info_logs = etl.fromcsv(name_logfile, delimiter='|')
        info_logs = etl.pushheader(info_logs, header_row)
        selected_info_logs = etl.select(info_logs,
                                        lambda rec: (rec.type_msg.strip() == 'MSG_USER' or
                                                    rec.type_msg.strip() == 'MSG_CHATBOT' or
                                                    rec.type_msg.strip() == 'MSG_WS_USER' or
                                                    rec.type_msg.strip() == 'MSG_WS_CHATBOT' or
                                                    rec.type_msg.strip() == 'MSG_WS_CHATBOT' or
                                                    rec.type_msg.strip() == 'USER_NAME' or
                                                    rec.type_msg.strip() == 'CHATBOT_NAME' or
                                                    rec.type_msg.strip() == 'INIT_CHAT' or
                                                    rec.type_msg.strip() == 'CLOSING')
                                                    and rec.level.strip() == 'INFO'
                                        )

        dialog_xml = None
        num_dialogs = 0
        turns_counter = 1
        bool_use_buffer = True
        buffer_turns = []  # Keep turns until the chatbot name and user name are set
        for line_log, turn in enumerate(selected_info_logs[1:]):  # Skip reading the header
            # print '... processing line ' + str(line_log+1)
            turn_dict = dict((header_row[y], x) for y, x in enumerate(turn))
            if 'INIT_CHAT' in turn_dict['type_msg']:
                buffer_turns = []
                turns_counter = 1
                num_dialogs += 1
                dialog_xml = SubElement(dialogues_xml, 'dialog', {'id': str(num_dialogs)})
                bool_use_buffer = True
                print ('Start processing dialog: %s' % num_dialogs)
            elif 'CHATBOT_NAME' in turn_dict['type_msg']:
                system_name = SubElement(dialog_xml, 'system_name')
                system_name.text = name_chatbot
            elif 'USER_NAME' in turn_dict['type_msg']:
                user_name = SubElement(dialog_xml, 'user_name')
                user_name.text = name_user
                if len(buffer_turns) > 0:  # Save the buffer and stop using it
                    for turn_xml in buffer_turns:
                        dialog_xml.append(turn_xml)
                    buffer_turns = []
                bool_use_buffer = False

            elif 'CLOSING' in turn_dict['type_msg']:
                if len(buffer_turns) > 0:
                    for turn_xml in buffer_turns:
                        dialog_xml.append(turn_xml)
                    buffer_turns = []
                print ('End processing dialog')
            else:
                turn_xml = Element('turn', {'id': str(turns_counter)})
                speaker_info = SubElement(turn_xml, 'speaker')
                if 'CHATBOT' in turn_dict['type_msg']:
                    speaker_info.text = 'SYSTEM'
                else:
                    speaker_info.text = 'USER'

                utterance_info = SubElement(turn_xml, 'utterance')
                if 'WS' in turn_dict['type_msg']:
                    jmsg = eval(turn_dict['msg'])
                    if 'USER' in turn_dict['type_msg']:
                        utterance_info.text = process_text(jmsg['payload'], name_chatbot, name_user)
                    else:
                        utterance_info.text = process_text(jmsg['payload'][0], name_chatbot, name_user)
                else:
                    utterance_info.text = process_text(turn_dict['msg'], name_chatbot, name_user)

                timestamp_info = SubElement(turn_xml, 'timestamp')
                timestamp_info.text = process_text(turn_dict['date'])
                if bool_use_buffer is True:
                    buffer_turns.append(turn_xml)
                else:
                    dialog_xml.append(turn_xml)
                turns_counter += 1

        with codecs.open(out_xml_file, 'w', 'utf-8') as f:
            f.write(prettify(dialogues_xml))

        print ('Successful conversion. Please submit the XML and Log files to the organizers')

    except Exception as e:
        print ('ERROR creating XML (%s) from Log file (%s)' %(out_xml_file, name_logfile))
        print ('Please submit the original Log files to the organizers')
        print("Unexpected error: %s" % sys.exc_info()[0])
        traceback.print_exc(file=sys.stdout)


if __name__ == '__main__':
    fntCreateXMLFromLogs()