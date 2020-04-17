# Copyright 2020 SuperDARN Canada, University of Saskatchewan
# Author: Kevin Krieger & Ashton Reimer
"""
Utilities for plotting and listening to DMAP IQ files

Exceptions
----------

Functions
---------
plot_iq

iq_to_wav

References: https://www.garykessler.net/library/file_sigs.html
"""
import pydarn
import binascii
import numpy as np
import datetime as dt
import soundfile
import matplotlib.pyplot as plt
import argparse as ap
import os


def iq_to_wav(records, save_directory, sequences_to_play=None):
    """
    Create one wav file for all records.

    This should plot the real and imag (I and Q) data in the left
    and right channels so you can listen in stereo (not yet implemented)!
    The sampling rate is currently hard-coded at 3333Hz,
    this should be fixed to play at the actual sampling rate, for most files it will be correct.
    :param records: pydarn iqdat records, as returned from read_iqdat()
    :param save_directory: Filepath to save the wav files to
    :param sequences_to_play: up to how many sequences should be written to wav file for each record?
    :return:
    """
    first = records[0]
    stid = first['stid']
    radar_abbrev = pydarn.SuperDARNRadars.radars[stid].hardware_info.abbrev
    record_datetime = dt.datetime.strptime(first['origin.time'], "%a %b %d %H:%M:%S %Y")
    record_datetime = record_datetime.strftime("%Y%m%d.%H%M.%S")
    wav_filename = save_directory + '/' + record_datetime + '.' + radar_abbrev + \
                   '.bm' + str(first['bmnum']) + '.wav'

    # Signals will contain the actual wav file samples
    signals = []
    for record in records:
        if sequences_to_play is None:
            # All of them!
            sequences_to_play = int(record['seqnum'])
        if not isinstance(sequences_to_play, int):
            print("Need to specify an integer for sequences_to_play, plotting all.")
            sequences_to_play = record['seqnum']
        sequences_to_play = max(sequences_to_play, record['seqnum'])

        data = np.copy(record['data'])
        data = data.reshape((int(record['seqnum']), int(record['chnnum']), int(record['smpnum']), 2))
        for sequence in range(sequences_to_play):
            iq_real = np.array([x[0] for x in data[sequence][0]])
            iq_imag = np.array([x[1] for x in data[sequence][0]])
            # TODO: Stereo sound with real and imag in the two channels
            signals.extend(iq_real)

    # TODO: Don't hardcode the sampling rate at 3333
    soundfile.write(wav_filename, signals, 3333, 'PCM_16')


def plot_iq(records, save_directory, sequences_to_plot=None):
    """
    Plot the records in a nice way.

    That's nice. Optionally specify up to how many sequences
    to plot for each record. It will plot them in order up to the number specified or all
    of the sequences, whichever is less.
    :param records: pydarn iqdat records, as returned from read_iqdat()
    :param save_directory: Filepath to save the plots to
    :param sequences_to_plot: up to how many sequences should be plotted for each record?
    :return:
    """
    # TODO: Print out progress bar, because this is slow.
    for record in records:
        stid = record['stid']
        radar_abbrev = pydarn.SuperDARNRadars.radars[stid].hardware_info.abbrev
        record_datetime = dt.datetime.strptime(record['origin.time'], "%a %b %d %H:%M:%S %Y")
        record_datetime = record_datetime.strftime("%Y%m%d.%H%M.%S")
        plot_filename = save_directory + '/' + record_datetime + '.' + radar_abbrev + \
                        '.bm' + str(record['bmnum']) + '.png'

        if sequences_to_plot is None:
            # Plot all of them!
            sequences_to_plot = int(record['seqnum'])
        if not isinstance(sequences_to_plot, int):
            print("Need to specify an integer for sequences_to_plot, plotting all.")
            sequences_to_plot = record['seqnum']
        sequences_to_plot = max(sequences_to_plot, record['seqnum'])

        # Need to know how many samples per tau (what samples could contain a tx pulse?)
        samps_per_tau = record['mpinc'] / record['smsep']
        # Determine which samples overlap with tx pulses
        blanked_samples = [record['skpnum'] - 1 + pulse * samps_per_tau for pulse in record['ptab']]

        fig = plt.figure(figsize=(11, 8.5))  # Regular 8.5" x 11" sheet of paper size
        figtop = 0.88
        figheight = 0.82 / sequences_to_plot
        data = np.copy(record['data'])

        data = data.reshape((int(record['seqnum']), int(record['chnnum']), int(record['smpnum']), 2))

        for sequence in range(sequences_to_plot):
            # Calculate positions of the data axis and colorbar axis for the current parameter
            # and then add them to the figure. position is [left, bottom, width, height] in fractions
            # of figure width and height
            position = [0.1, figtop - figheight * (sequence + 1) + 0.05, 0.8, figheight]
            ax = fig.add_axes(position)

            if sequence is 0:
                title = 'Pulse Sequence IQ Data ' + radar_abbrev + ' Beam ' + \
                        str(record['bmnum']) + ' Tx Freq: ' + str(record['tfreq']) + \
                        'kHz  Time: ' + record_datetime
                ax.set_title(title)

            ax.set_xticklabels([])
            ax.set_yticklabels([])

            sample_numbers = range(record['smpnum'])

            iq_real = np.array([x[0] for x in data[sequence][0]])
            iq_imag = np.array([x[1] for x in data[sequence][0]])

            ax.plot(sample_numbers, iq_real, 'k')
            ax.plot(sample_numbers, iq_imag, 'r')
            ax.set_xlim([0, record['smpnum']])
            ax.set_ylim([-300, 300])  # TODO: Get rid of magic numbers... maybe auto range for entire plot
            ax.set_ylabel(str(sequence))

        position = [0.1, figtop - figheight * sequences_to_plot + 0.02, 0.8, 0.03]
        ax = fig.add_axes(position)

        # Now add the transmit pules axis on the bottom
        const = 0.5 * (record['smpnum'] + 100) / float(record['smpnum'])
        for x in blanked_samples:
            time = np.array([x - const, x - const, x + const, x + const])
            amp = np.array([0, 1, 1, 0])
            ax.fill(time, amp, color='black')
            ax.set_xlim([0, record['smpnum']])
            ax.set_ylabel('TX')
            ax.set_yticklabels([])

        fig = plt.gcf()
        fig.savefig(plot_filename)
        plt.close(fig)


def get_stats_from_records(pydarn_records):
    """
    Return a string of various important or nice to know info from the pydarn records
    :param pydarn_records: pydarn records from a call to pydarn.SDarnRead(...).read_iqdat()
    :return: String of various stats
    """
    first = pydarn_records[0]
    last = pydarn_records[-1]
    stid = first['stid']
    hw_info = pydarn.SuperDARNRadars.radars[stid].hardware_info
    stats = "Number of records: {}\r\n".format(len(pydarn_records))
    stats += "Radar: {} Station ID: {}\r\n".format(hw_info.abbrev, first['stid'])
    stats += "Start time: {}, end time: {}".format(first['origin.time'], last['origin.time'])
    return stats


def open_compressed_file(input_filename):
    """
    Check the input filename for compression style and return an uncompressed file handle
    This method uses magic numbers inherent to various file types, and imports what it needs,
    when it needs it. The result is a filestream ready for pydarn.SDarnRead(returnval, True).
    Note that SDarnRead takes a boolean value True if the first argument is a filestream.
    :param input_filename: Path to a file to test and uncompress
    :return: File stream for the uncompressed file
    """
    # Normally, IQ files are gzip compressed, try that first.
    # Note that there are other ways to do this, but they rely on python versions >= 3.7
    # For various file types, magic numbers are below:
    # gzip:     0x1F8B08
    # bzip:     0x425A68
    # tar.z:    0x1F9D OR 0x1FA0
    # lha,lzh:  0x2D6C68
    # 7z:       0x377ABCAF271C
    # zip:      0x504B4C495445  *** At 30 byte offset ***
    # zip:      0x504B537058    *** At 526 byte offset ***
    # rar:      0x526172211A0700 OR 0x526172211A070100
    with open(input_filename, 'rb') as file_to_test:
        magic_number = binascii.hexlify(file_to_test.read(3))

    if magic_number == b'1f8b08':  # Note that you need lowercase hex chars
        import gzip
        return gzip.open(input_filename).read()
    elif magic_number == b'425a68':
        import bz2
        return bz2.open(input_filename).read()
    else:
        return open(input_filename, 'rb').read()  # You need to open this in binary mode
    # TODO: Possible other compression types
    # TODO: catch any exceptions this may raise


if __name__ == "__main__":
    parser = ap.ArgumentParser('Utility to plot and listen to DMAP IQ files')
    parser.add_argument('--debug', help='Print out debugging info', action='store_true')
    parser.add_argument('--plot', help='Generate plots of each record',
                        action='store_true', default=False)
    parser.add_argument('--listen', help='Generate WAV files of the DMAP IQ records',
                        action='store_true', default=False)
    parser.add_argument('--plots-dir', help='Output directory to store plots',
                        action='store', default='iq_plots')
    parser.add_argument('--wav-dir', help='Output directory to store WAV files',
                        action='store', default='iq_wav')
    parser.add_argument('input_file', help='Input IQ file to plot or listen to')
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        raise FileNotFoundError("Cannot find input file: {}".format(args.input_file))

    # Determine if the file is unzipped, gzipped or bzipped, and open it to get a stream
    iq_stream = open_compressed_file(args.input_file)

    # Use pydarn to get a reader, then the iqdat records, using the iq_stream
    # TODO: catch any exceptions this may raise
    iq = pydarn.SDarnRead(iq_stream, True)
    records = iq.read_iqdat()

    # Print out debug information if debug mode, or if neither plotting or listening
    if args.debug or not (args.plot or args.listen):
        print("Input file: {}\r\n".format(args.input_file))
        print(get_stats_from_records(records))
        print("")
        for key in records[0].keys():
            print(key)
        start_time = dt.datetime.strptime(records[0]['origin.time'], "%a %b %d %H:%M:%S %Y")
        print("Start time: {}".format(start_time.strftime("%Y%m%d.%H%M.%S")))

    # TODO:  Try to calculate size of outputs/length of time it may take, and print it out.
    if args.plot:
        print("Plotting each IQ record from {}".format(args.input_file))
        print(" ** NOTE ** This takes a long time, go for a walk and stretch")
        if not os.path.isdir(args.plots_dir):
            # Create the directory
            os.makedirs(args.plots_dir)
        # Make plots!
        plot_iq(records, args.plots_dir)

    if args.listen:
        print("Generating WAV files for each IQ record from {}".format(args.input_file))
        if not os.path.isdir(args.wav_dir):
            # Create the directory
            os.makedirs(args.wav_dir)
        # Make WAV files!
        iq_to_wav(records, args.wav_dir)
