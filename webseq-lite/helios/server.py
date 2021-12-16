###################################################################
# Script Name	: server.py
# Description	: This is THE master file. This launches the Flask server.
#               : Contains all the celery tasks as well.
# Args          : None.
# Author        : Milind Agarwal
# Lab           : Markle Lab, JHBSPH
# Email         : magarw10@jhu.edu
###################################################################


# Stage 1 Imports: Uploading data through POST request
import os
import shutil
from flask import Flask, flash, request, redirect, url_for, render_template
from flask import send_from_directory, jsonify, send_file
from flask import Markup

import random
import time

from werkzeug.utils import secure_filename

from os import listdir
from os.path import isfile, join

# Stage 3 Imports: Executing Cleaning Script
import pandas as pd

import sys
sys.stdout.flush()
import zipfile

# Extra imports requred from ANNOTATION step.
import numpy as np
import glob


# Importing json
from requests_toolbelt import MultipartEncoder
import json

## Importing subprocess to call BASH Scripts
import subprocess
from subprocess import check_output,CalledProcessError


import matplotlib
import matplotlib.pyplot as plt
from pandas import ExcelWriter
from pandas import ExcelFile

import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot
import plotly.io as plio


# Parallel code imports
import dask.dataframe as dd
from collections import Counter
from itertools import compress
import json

import datetime


UPLOAD_FOLDER = './temp/'

# Color and key dictionaries for 1000G Ancestry Plots.

def create_app():
    app = Flask(__name__)
    return app


app = create_app()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


from celery import Celery
from celery.exceptions import Ignore
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# app.config['CORS_HEADER'] = 'Content-Type'


######
# CELERY -- ASYNCHRONOUS WORKER QUEUE SETUP
# ######
# from celery import Celery

# This URL tells Celery where the broker service is running. If you run something
# other than Redis, or have the broker on a different machine, then you will need
# to change the URL accordingly.
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
#
# # The CELERY_RESULT_BACKEND option is only necessary if you need to have Celery
# # store status and results from tasks.
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
#
# # initialized by creating an object of class Celery
# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)
########


def allowed_file(filename):
    with open('./defaults.json') as json_file:
        default = json.load(json_file)
        # Allowed Extensions for File Uplading. If a file is not being uploaded, check its
        # extension first, and cross verify with this list

        ALLOWED_EXTENSIONS = default["ALLOWED_EXTENSIONS"]
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


###############################################################################
#####################        APP ROUTES    --- GENERAL          ###############
###############################################################################
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

# route = endpoint
# decorator
@app.route('/') # home --> homies.com   api.spotify.com/
def my_home_page():
    return render_template('home.html')

# www.homies.com/contactus
@app.route('/contactus')
def my_contact_page():
    return render_template('contact.html')

###############################################################################
#####################        APP ROUTES    --- TEST          ###################
###############################################################################

@app.route('/genemania' ,methods=['POST', 'GET'])
def my_pathway_page():
    if request.method == 'POST':
        print("## POST Request sent to /geneMANIAURL. Now going to check for request data ")

        # check if the post request has the file part

        fileArray = []
        for x in request.files:
            fileArray.append(request.files[x])

        if len(fileArray) == 0:
            print('No selected file')
            return redirect(request.url)

        print("Here")
        home = os.getcwd()
        print(home)
        tempdir = home + '/temp'
        print(tempdir)
        shutil.rmtree(tempdir)
        os.mkdir('temp')

        for file in fileArray:
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename + "  GENEMANIA")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                print("Bad extension")
                return {}

        print("## All files saved in the TEMP directory.")

        mypath = tempdir + '/'

        # 1. Load up all the files from the temp folder.
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        # Do the processing here, and pass back a response object.
        print(mypath + onlyfiles[0])
        if onlyfiles[0].endswith('.csv'):
            x = pd.read_csv(mypath + onlyfiles[0], dtype='str')
            x = x.reset_index(drop=True)

        elif onlyfiles[0].endswith('xlsx'):
            x = pd.read_excel(mypath + onlyfiles[0], dtype='str')
            x = x.reset_index(drop=True)


        os.chdir(home)

        return jsonify("/".join(list(set(list(x['Gene.refGene'])))))

    return render_template('pathway.html')


@app.route('/annovar_option')
def my_annovar_options_page():
    return render_template('annovar_options.html')

@celery.task(bind=True)
def execute_fastqtovcf(self, onlyfiles, home, readgroup):
    self.update_state(state='PROGRESS', meta={'current':2, 'total':100, 'status':'Starting process'})

    length = len(onlyfiles)
    os.chdir(home)
    fastqtovcfpath = '../../../webseq_sandbox/forfastqtovcf/fastqtovcf'
    fastq1 = onlyfiles[0]
    fastq2 = onlyfiles[1]
    os.chdir(fastqtovcfpath)
    #readgroupvalue=readgroupdata['value']

    # TODO: Also pass in read group retrieved from request as an argument to BASH

    # TODO:
    pass_arg = ['bash','bwamem.sh', fastq1, fastq2, readgroup]
    print("This is what is going to be excuted")
    print(os.getcwd())
    print(pass_arg)

    # PROGRESS BARS: Check for total steps, and how many steps you want to fulfill.

    self.update_state(state='PROGRESS', meta={'current': 30, 'total':100, 'status':'Bwa mem completed'})
    subprocess.check_call(pass_arg)




    pass_arg = ['bash','markduplicates.sh', readgroup]
    print("This is what is going to be excuted")
    print(os.getcwd())
    print(pass_arg)



    self.update_state(state='PROGRESS', meta={'current': 45, 'total':100, 'status':'Marking duplicates completed'})
    subprocess.check_call(pass_arg)



    pass_arg = ['bash','basequality.sh', readgroup]
    print("This is what is going to be excuted")
    print(os.getcwd())
    print(pass_arg)



    self.update_state(state="PROGRESS", meta={'current': 70, 'total':100, 'status':'Base Quality Score generation completed'})
    subprocess.check_call(pass_arg)


    pass_arg = ['bash','haplotypecaller.sh', readgroup]
    print("This is what is going to be excuted")
    print(os.getcwd())
    print(pass_arg)



    self.update_state(state="PROGRESS", meta={'current': 95, 'total':100, 'status':'Variant calling completed'})
    subprocess.check_call(pass_arg)


    # At this point, be done with broken up pipeline.sh all commands
    # TODO: Rename BAM and VCF accordingly (using fastq1 and fastq2 prefix)

    os.chdir(home)

    self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Completed Generating VCFs for each FASTQ you uploaded'})

    # Move the files to Desktop folder.
    args = ['bash','vcfdownload.sh']
    subprocess.check_call(args)


    return {'current':100, 'total':100, 'status': 'Task Completed!', 'result': 100}



@app.route('/fastqtovcf', methods=['POST', 'GET'])
def my_fastqtovcf_task():
    if request.method == 'POST':
        print("## POST Request sen to /fastqtovcfurl. Now going to check for request data ", flush=True)
        print(request.files, flush=True)
        fileArray = []
        for x in request.files:
            fileArray.append(request.files[x])

        # TODO: Retrieve read group variable from the POST request. Check Modes app route for example
        readgroup = request.form.get('readgrouptext')

        print(readgroup, flush=True)

        print(fileArray, flush=True)

        if len(fileArray) == 0:
            print('No selected file')
            return redirect(request.url)

        print("Here")
        home=os.getcwd()
        selectedfiles=[]

        for file in fileArray:
            if file.filename == '':
                print("No selected file")
                return redirect(request.url)
            #print(allowed_file(file.filename))
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename + " Fastq files ", flush=True)
                selectedfiles.append(filename)
                print(">>>>>>>>>>>>>>>>>>>>")
                print(selectedfiles, flush=True)
                # file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        print(selectedfiles, flush=True)
        os.chdir(home)
        mypath ='../../../webseq_sandbox/forfastqtovcf/fastqfiles/'
        print("#########################")
        os.chdir(mypath)
        fastqfilespath = os.getcwd()
        print(fastqfilespath, flush=True)
        print("##########################")

        # if len(selectedfiles) > 2:
        #     os.chdir(fastqfilespath)
        #     pass_arg = ['bash', 'mergefastq.sh', readgroup]
        #     subprocess.check_call(pass_arg)
        #     combinefastq = 'combinefastq'
        #     os.chdir(combinefastq)
        #     combinefastqpath = os.getcwd()
        #     print("*****************")
        #     print(combinefastqpath)
        #     print("*****************")
        #
        #     os.chdir(home)
        #     onlyfiles = []
        #     for f in listdir(combinefastqpath):
        #         if 'fastq' in f:
        #             onlyfiles.append(combinefastqpath+'/'+f)
        #
        #     print(onlyfiles)
        #     print ("Calling celery method")
        #     os.chdir(home)
        #     task = execute_fastqtovcf.delay(onlyfiles, home, readgroup)
        #
        #     os.chdir(home)
        #     return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}
        # else:
        os.chdir(home)
        onlyfiles=[]
        print(onlyfiles, flush=True)
        for f in listdir(fastqfilespath):
            if f in selectedfiles:
                onlyfiles.append(fastqfilespath+"/"+f)
                    #onlyfiles = [fastqfilespath +'/' + f for f in listdir(fastqfilespath) if isfile(join(fastqfilespath, f))]
        print(onlyfiles, flush=True)
        print("Calling CELERY method.")
        os.chdir(home)
        task = execute_fastqtovcf.delay(onlyfiles, home, readgroup)

        os.chdir(home)
        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

    return render_template('/fastq.html')

@celery.task(bind=True)
def execute_genepanel(self, onlyfiles, home):

    self.update_state(state='PROGRESS', meta={'current':2, 'total':100, 'staus':'Starting process'})

    length = len(onlyfiles)
    iterate = 0
    file1_orig = onlyfiles[0]
    file2_orig = onlyfiles[1]

    os.chdir('./temp')
    path = os.getcwd()

    file1 = path+'/' + file1_orig
    file2 = path+'/' + file2_orig

    os.chdir(home)
    print("*****************")
    print(os.getcwd())
    print("*****************")
    os.chdir('./genepanel')
    print("####################")
    filteringwithgenespath = os.getcwd()
    print(filteringwithgenespath)
    print("######################")

    pass_args = ['python3', filteringwithgenespath+"/"+'FilteringWithGenes.py', file2, file1]
    print("This is what's going to be executed..")
    print(os.getcwd())
    print(pass_args)

    iterate = iterate + 1
    self.update_state(state='PROGRESS', meta={'current': iterate * 100/(2*length), 'total': 100, 'status': 'Starting to process a new VCF'})

    subprocess.check_call(pass_args)

    # Update the progress bar here.
    iterate = iterate + 1
    self.update_state(state='PROGRESS', meta={'current': iterate * 100/(2*length), 'total': 100, 'status': 'Completed another VCF file succssfully. :) '})

    os.chdir(home)
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print(os.getcwd())
    pass_arg = ['bash', 'movegenepanel.sh']
    subprocess.check_call(pass_arg)
    os.chdir(home)

    self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Completed Generating ANNOVARs for each VCF you uploaded'})
    return {'current':100, 'total':100, 'status': 'Task Completed!', 'result': 100}

##gene panel app.route
@app.route('/gene', methods=['POST', 'GET'])
def my_genepanel_task():
    if request.method == 'POST':
        print("## POST Request sent to /geneurl. Now going to check for request data.")
        print(request.files)
        fileArray=[]
        for x in request.files:
            fileArray.append(request.files[x])

        print(fileArray)

        if len(fileArray) == 0:
            print("No selected file")
            return redirect(request.url)

        print("Here")
        home = os.getcwd()
        print(home)
        tempdir = home + '/temp'
        print(tempdir)
        shutil.rmtree(tempdir)
        os.mkdir('temp')

        for file in fileArray:
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename + "12345")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                print("BAD Extension")
                return {}

        print('## All files saved in the TEMP directory.')

        mypath = tempdir + '/'

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        print("Files have been saved")
        print(onlyfiles)

        task = execute_genepanel.delay(onlyfiles, home)

        os.chdir(home)
        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

    return render_template('/genes.html')


@celery.task(bind=True)
def execute_onevcf(self, onlyfiles, home):
    self.update_state(state='PROGRESS', meta={'current': 2, 'total': 100, 'status': 'Starting process'})

    length = len(onlyfiles)
    iterate = 0
    for file in onlyfiles:
        os.chdir(home)

        # os.chdir('./annovar')
        os.chdir('../../../webseq_sandbox/ANNOVAR/anno_scripts')

        filename = home + '/temp/' + file
        # Execute the shell script with the parameter.
        pass_arg = ['./script.sh', filename]

        # Update the progress bar here.
        iterate = iterate + 1
        self.update_state(state='PROGRESS', meta={'current': iterate * 100/(2*length), 'total': 100, 'status': 'Starting to process a new VCF'})

        subprocess.check_call(pass_arg)

        # Update the progress bar here.
        iterate = iterate + 1
        self.update_state(state='PROGRESS', meta={'current': iterate * 100/(2*length), 'total': 100, 'status': 'Completed another VCF file succssfully. :) '})

    os.chdir(home)
    pass_arg = ['./movefiles.sh']
    subprocess.check_call(pass_arg)

    os.chdir(home)

    self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Completed Generating ANNOVARs for each VCF you uploaded'})
    return {'current':100, 'total':100, 'status': 'Task Completed!', 'result': 100}


@celery.task(bind=True)
def execute_twovcf(self, onlyfiles, home):

    self.update_state(state='PROGRESS', meta={'current': 2, 'total': 100, 'status': 'Starting process'})

    length = len(onlyfiles)
    iterate = 0
    file1_orig = onlyfiles[0]
    file2_orig = onlyfiles[1]
    file1 = home + '/temp/' + file1_orig
    file2 = home + '/temp/' + file2_orig

    os.chdir(home)
    # os.chdir('./annovar')
    os.chdir('../../../webseq_sandbox/ANNOVAR/anno_scripts')

    # First, execute the python script.
    pass_arg = ['python3', 'merge.py', file1, file2]
    subprocess.check_call(pass_arg)

    os.mkdir(home + '/temp/res')

    onlyfiles = [f for f in listdir(home + '/temp/') if isfile(join(home + '/temp/', f))]

    for file_name in onlyfiles:
        if (file_name != file1_orig and file_name != file2_orig):
            #Then its the new file
            os.rename(home + '/temp/' + file_name, home + '/temp/res/' + file_name )

    filex = [f for f in listdir(home + '/temp/res/') if isfile(join(home + '/temp/res/', f))]

    # Execute the shell script with the parameter.
    # Update the progress bar here.
    iterate = iterate + 1
    self.update_state(state='PROGRESS', meta={'current': iterate * 100/(length), 'total': 100, 'status': 'Starting to process a new VCF'})

    pass_arg = ['./script2.sh', home + '/temp/res/' + filex[0]]
    subprocess.check_call(pass_arg)
    # Update the progress bar here.
    iterate = iterate + 1
    self.update_state(state='PROGRESS', meta={'current': iterate * 100/(length), 'total': 100, 'status': 'Completed another VCF file succssfully. :) '})


    # Moved this from line 302 to line 297 on Aug 27, 2019
    os.chdir(home)

    # Delete the VCF file from the results directory here..
    pass_arg = ['./deleteVCF.sh']
    subprocess.check_call(pass_arg)

    os.chdir(home)

    self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Completed Generating ANNOVARs for each VCF you uploaded'})

    return {'current':100, 'total':100, 'status': 'Task Completed!', 'result': 100}

@app.route('/onevcf', methods=['POST', 'GET'])
def my_onevcf_task():
    if request.method == 'POST':
        print("## POST Request sent to /onevcfurl. Now going to check for request data ")
        print(request.files)
        # check if the post request has the file part
        # if 'cleanfile' not in request.files:
        #     print('No file part')
        #     return redirect(request.url)
        fileArray = []
        for x in request.files:
            fileArray.append(request.files[x])

        #fileArray = request.files.getlist('cleanfile')
        print(fileArray)
        # if user does not select file, browser also
        # submit an empty part without filename

        if len(fileArray) == 0:
            print('No selected file')
            return redirect(request.url)

        print("Here")
        home = os.getcwd()
        print(home)
        tempdir = home + '/temp'
        print(tempdir)
        shutil.rmtree(tempdir)
        os.mkdir('temp')

        for file in fileArray:
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename + "  12345")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                print("Bad extension")
                return {}

        print("## All files saved in the TEMP directory.")

        mypath = tempdir + '/'

        # 1. Load up all the files from the temp folder.
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        print("Files have been saved . ADIOS")
        print(onlyfiles)

        task = execute_onevcf.delay(onlyfiles, home)

        os.chdir(home)
        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

    # # GET REQUEST METHOD
    return render_template('/oneVCFannovar.html')

@app.route('/twovcf', methods=['POST', 'GET'])
def my_twovcf_task():
    if request.method == 'POST':
        print("## POST Request sent to /twovcfurl. Now going to check for request data ")
        print(request.files)
        # check if the post request has the file part
        # if 'cleanfile' not in request.files:
        #     print('No file part')
        #     return redirect(request.url)
        fileArray = []
        for x in request.files:
            fileArray.append(request.files[x])

        #fileArray = request.files.getlist('cleanfile')
        print(fileArray)
        # if user does not select file, browser also
        # submit an empty part without filename

        if len(fileArray) == 0:
            print('No selected file')
            return redirect(request.url)

        print("Here")
        home = os.getcwd()
        print(home)
        tempdir = home + '/temp'
        print(tempdir)
        shutil.rmtree(tempdir)
        os.mkdir('temp')

        for file in fileArray:
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename + "  12345")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                print("Bad extension")
                return {}

        print("## All files saved in the TEMP directory.")

        mypath = tempdir + '/'

        # 1. Load up all the files from the temp folder.
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        print("Files have been saved . ADIOS")
        print(onlyfiles)

        task = execute_twovcf.delay(onlyfiles, home)

        os.chdir(home)
        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

    # # GET REQUEST METHOD
    return render_template('/twoVCFannovar.html')


@app.route('/blacklist')
def my_blacklist_page():
    return render_template('blacklist.html')

@app.route('/gen_blacklist', methods=['POST', 'GET'])
def my_gen_blacklist_page():
    if request.method == 'POST':
        print("## POST Request sent to /gen_blacklistURL. Now going to check for request data ")
        # print(request.files)\
        CUTOFF = float(request.form.get('cutoff'))
        # Because it is a percentage, so now we're making it a fraction.
        CUTOFF = CUTOFF/100
        print(CUTOFF)
        # check if the post request has the file part
        # if 'cleanfile' not in request.files:
        #     print('No file part')
        #     return redirect(request.url)
        fileArray = []
        for x in request.files:
            fileArray.append(request.files[x])

        #fileArray = request.files.getlist('cleanfile')
        # print(fileArray)
        # if user does not select file, browser also
        # submit an empty part without filename

        if len(fileArray) == 0:
            print('No selected file')
            return redirect(request.url)

        print("Here")
        home = os.getcwd()
        print(home)
        tempdir = home + '/temp'
        print(tempdir)
        shutil.rmtree(tempdir)
        os.mkdir('temp')

        for file in fileArray:
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename + "  BLACKLIST")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                print("Bad extension")
                return {}

        print("## All files saved in the TEMP directory.")

        mypath = tempdir + '/'

        # 1. Load up all the files from the temp folder.
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        task = blacklist_generation.delay(mypath, onlyfiles, CUTOFF)

        os.chdir(home)
        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}


    return render_template('blacklist_generator.html')

@app.route('/apply_blacklist', methods=['POST', 'GET'])
def my_apply_blacklist_page():
    if request.method == 'POST':
        print("## POST Request sent to /apply_blacklistURL. Now going to check for request data ")

        fileArray = []
        for x in request.files:
            fileArray.append(request.files[x])

        if len(fileArray) == 0:
            print('No selected file')
            return redirect(request.url)

        print("Here")
        home = os.getcwd()
        print(home)
        tempdir = home + '/temp'
        print(tempdir)

        shutil.rmtree(tempdir)
        os.mkdir('temp')

        for file in fileArray:
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename + "  BLACKLIST APPLY")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                print("Bad extension")
                return {}

        print("## All files saved in the TEMP directory.")

        mypath = tempdir + '/'

        # The last append to the files is indeed the blacklist.
        blacklist_file_name = secure_filename(fileArray[-1].filename)

        # 1. Load up all the files from the temp folder.
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        ix = list(onlyfiles).index(blacklist_file_name)
        onlyfiles.pop(ix)

        print(onlyfiles)

        checksort = request.form.get('checkSort')
        task = apply_blacklist.delay(mypath, onlyfiles, blacklist_file_name, checksort)
        os.chdir(home)

        # wes_cleaning(home, mypath, onlyfiles)
        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

    return render_template('blacklist_apply.html')


###############################################################################
#####################        APP ROUTES    --- WES          ###################
###############################################################################

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = wes_cleaning.AsyncResult(task_id)
    if task.state == 'PENDING':
        print("PENDING")
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        print("NOT FAILED> ")
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            print("DONE?")
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@app.route('/clean', methods=['POST', 'GET'])
def my_cleaning_task():
    if request.method == 'POST':
        print("## POST Request sent to /cleaningurl. Now going to check for request data ")
        print(request.files)
        # check if the post request has the file part
        # if 'cleanfile' not in request.files:
        #     print('No file part')
        #     return redirect(request.url)
        fileArray = []
        for x in request.files:
            fileArray.append(request.files[x])

        #fileArray = request.files.getlist('cleanfile')
        print(fileArray)
        # if user does not select file, browser also
        # submit an empty part without filename
        print("Here")
        home = os.getcwd()
        print(home)
        tempdir = home + '/temp'
        print(tempdir)

        if len(fileArray) == 0:
            print('No selected file. This means that there were cookies from a previous step. ')


        else:
            shutil.rmtree(tempdir)
            os.mkdir('temp')

            for file in fileArray:
                if file.filename == '':
                    print('No selected file')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    print(filename + "  12345")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    print("Bad extension")
                    return {}

        print("## All files saved in the TEMP directory.")

        mypath = tempdir + '/'

        # 1. Load up all the files from the temp folder.
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        include =request.form['include']

        task = wes_cleaning.delay(home, mypath, onlyfiles, include)

        # MODIFYING CELERY: RETURN VALUEEEEE
        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

    # # GET REQUEST METHOD
    print("## GET Request sent to /cleaningurl. Now redirecting to /")
    return render_template('/cleaning.html')


@app.route('/annotate', methods=['POST', 'GET'])
def my_annotating_task():
    if request.method == 'POST':

        # check if the post request has the file part
        #can I blur this out? YEP, FOR COOKIES, I HAVE TO.
        # if 'annotatefile' not in request.files:
        #     print('No file part')
        #     return redirect(request.url)

        fileArray = request.files.getlist('annotatefile')
        print(fileArray)
        # if user does not select file, browser also
        # submit an empty part without filename


        home = os.getcwd()
        tempdir = home + '/temp'
        if len(fileArray) == 0:
            print('No selected file. This means that there were cookies from a previous step. ')
            # return redirect(request.url)

        else:
            shutil.rmtree(tempdir)
            os.mkdir('temp')

            for file in fileArray:
                if file.filename == '':
                    print('No selected file')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    print(
                        filename + ": File extension supported. Will try to save it to the server.")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("## All files saved in the TEMP directory.")

        mypath = tempdir + '/'

        # 1. Load up all the files from the temp folder.
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        # Once the files are read, execute our python script, and save back the
        # annotated data. This is the most time consuming task of this call.

        task = annotate_my_directory.delay(home, mypath, onlyfiles)

        # MODIFYING CELERY: RETURN VALUEEEEE
        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

    # # GET REQUEST METHOD
    print("## Now redirecting to /annotate.html")
    return render_template('/annotate.html')


@app.route('/filtering', methods=['POST', 'GET'])
def my_filtering_task():
    if request.method == 'POST':
        # print("## POST Request sent to /annotatinggurl. Now going to check for request data ")
        # check if the post request has the file part


        fileArray = request.files.getlist('filterfile')
        print(fileArray)
        # if user does not select file, browser also
        # submit an empty part without filename

        gdi = request.form.get('gdiThreshold')
        maf = request.form.get('mafThreshold')
        mafCol = request.form.get('mafColumns')


        home = os.getcwd()
        tempdir = home + '/temp'
        mypath = tempdir + '/'


        if len(fileArray) == 0:
            print('No selected file. This means that there were cookies from a previous step. ')

            # return redirect(request.url)
        else:
            shutil.rmtree(tempdir)
            os.mkdir('temp')

            for file in fileArray:
                if file.filename == '':
                    print('No selected file')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    print(
                        filename + ": File extension supported. Will try to save it to the server.")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            print("## All files saved in the TEMP directory.")

        # 1. Load up all the files from the temp folder.
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        # Once the files are read, execute our python script, and save back the
        # annotated data. This is the most time consuming task of this call.
        print('GDI: ', gdi, ' ', type(gdi))
        task = filter_my_directory.delay(home, mypath, onlyfiles, gdi, maf, mafCol)

        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

    # # GET REQUEST METHOD
    print("## Now redirecting to /filter.html")
    return render_template('/filter.html')


@app.route('/modes', methods=['POST', 'GET'])
def my_modes_task():
    if request.method == 'POST':
        print("## POST Request sent to /modesurl. Now going to check for request data ")
        zygs = request.form['zyg']
        zyglist = zygs.split(',')

        conf = request.form['config']
        print(conf)
        confList = conf.split(',')

        for i in range(0,3):
            if confList[i] == 'true':
                confList[i] = True;
            elif confList[i] == 'false':
                confList[i] = False;

        # This is the patient number, if compHet was selected..
        confList[-1] = int(confList[-1])

        fileArray = []
        for x in request.files:
            fileArray.append(request.files[x])

        print("Changing directories to read TEMP")
        home = os.getcwd()
        print(home)
        tempdir = home + '/temp'
        print(tempdir)

        mypath = tempdir + '/'

        # This will happen if we're just "PUSHING FORWARD..."
        if len(fileArray) == 0:
            print('No selected file. This means that there were cookies from a previous step. ')
            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        else:
            shutil.rmtree(tempdir)
            os.mkdir('temp')

            # Need to save it to the temp directory.
            onlyfiles = []
            for file in fileArray:
                if file.filename == '':
                    print('No selected file')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    print(filename + "  12345")
                    onlyfiles.append(filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            print("## All uploaded saved in the TEMP directory.")
            print(onlyfiles)


        # 1. Load up all the files from the temp folder. This is flipping the order of my files.
        # onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        #
        # # Reversing is not helping, I need to force the order the name was read in.
        # onlyfiles = onlyfiles[::-1]

        patient = zyglist[0]
        family = zyglist[1:]
        zyglist = [patient, family]

        task = modesOfInheritance.delay(mypath, onlyfiles, zyglist, confList);
        os.chdir(home)
        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

    # # GET REQUEST METHOD
    print("## GET Request sent to /modesurl. Now redirecting to /")
    return render_template('/modes_of_inheritance.html')


@app.route('/unbiasedcohort', methods=['POST', 'GET'])
def my_unbiasedcohort_task():
    if request.method == 'POST':
        # print("## POST Request sent to /annotatinggurl. Now going to check for request data ")
        # check if the post request has the file part
        # if 'unbiasedcohortfile' not in request.files:
        #     print('No file part')
        #     return redirect(request.url)

        maf = request.form['mafThreshunbcohort']
        mafCol = request.form.get('mafColumnsSel')

        print("MAFFFF : " + str(maf))
        print("COLLLLL: " + mafCol)
        fileArray = []
        for x in request.files:
            fileArray.append(request.files[x])

        # fileArray = request.files.getlist('unbiasedcohortfile')
        # print(fileArray)
        if len(fileArray) == 0:
            print('No selected file')
            return redirect(request.url)
        # if user does not select file, browser also
        # submit an empty part without filename

        #gdi = request.form.get('gdiThreshold')
        #maf = request.form.get('mafThreshold')
        #mafCol = request.form.get('mafColumns')

        home = os.getcwd()
        tempdir = home + '/temp'
        shutil.rmtree(tempdir)
        os.mkdir('temp')

        for file in fileArray:
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename + "  12345")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        print("## All files saved in the TEMP directory.")
        mypath = tempdir + '/'

        # 1. Load up all the files from the temp folder.
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        print("Here")
        print("Calling read cohort now")



        task = readcohortfiles.delay(mypath, onlyfiles, mafCol, maf)

        os.chdir(home)

        # Once the files are read, execute our python script, and save back the
        # annotated data. This is the most time consuming task of this call.
        #filter_my_directory(home, mypath, onlyfiles, gdi, maf, mafCol);

        # Ajax call returns success here, and we change some HTML on the screen, through the JS

        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

    # # GET REQUEST METHOD
    print("## Now redirecting to /unbiasedcohort.html")
    return render_template('/unbiased_cohort.html')

@app.route('/biasedcohort', methods=['POST', 'GET'])
def my_biasedcohort_task():
    if request.method == 'POST':
        # print("## POST Request sent to /annotatinggurl. Now going to check for request data ")
        # check if the post request has the file part
        print(request.form.get('data', None))
        fileArray = request.files.getlist('biasedcohortfile')
        gene = request.form['geneName']
        maf = request.form['mafThreshbcohort']
        print("Here's the threshold I'm getting: "  + maf)
        mafCol = request.form.get('mafColumnsSel')

        print('GDI: ', gene)
        print('MAF Col: ', mafCol)
        print('MAF: ', maf)

        if len(fileArray) == 0:
            print('No selected file')
            return redirect(request.url)

        home = os.getcwd()
        tempdir = home + '/temp'
        shutil.rmtree(tempdir)
        os.mkdir('temp')

        for file in fileArray:
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(
                    filename + ": File extension supported. Will try to save it to the server.")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        print("## All files saved in the TEMP directory.")

        mypath = tempdir + '/'



        # 1. Load up all the files from the temp folder.
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        print(onlyfiles)

        task = biased_cohort_analysis.delay(mypath, onlyfiles, gene, mafCol, maf)

        os.chdir(home)

        # Once the files are read, execute our python script, and save back the
        # annotated data. This is the most time consuming task of this call.
        #filter_my_directory(home, mypath, onlyfiles, gdi, maf, mafCol);

        # Ajax call returns success here, and we change some HTML on the screen, through the JS

        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

    # # GET REQUEST METHOD
    print("## Now redirecting to /biasedcohort.html")
    return render_template('/biased_cohort.html')


@app.route('/igvinfo', methods=['POST', 'GET'])
def get_igv_info():
    if request.method == 'POST':

        home = os.getcwd()
        tempdir = home + '/temp'
        mypath = tempdir + '/'

        # 1. Load up the file from the temp folder.
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        # New code that needs to be incorporated.

        if onlyfiles[0].endswith('.csv'):
            f = open(mypath + onlyfiles[0])
            cols = f.readline().split(',')
            data_full = pd.read_csv(mypath + onlyfiles[0], engine='python', names = cols)
            data_full = data_full.reset_index(drop=True)

        elif onlyfiles[0].endswith('xlsx'):
            data_full = pd.read_excel(mypath + onlyfiles[0] ,encoding=sys.getfilesystemencoding())
            data_full = data_full.reset_index(drop=True)

        #### RETURN THIS ONE....
        num_rows_query = data_full.shape[0]

        try:
            x = pd.read_csv('./bamFilesFullPaths.txt', header=None)
            bam_length = len(x)
        except:
            bam_length = -1;

        return jsonify([num_rows_query, bam_length])

# @app.route('/visualize', methods=['POST', 'GET'])
# def my_visualizer_page():
#     if request.method == 'POST':
#
#         mask = 0
#         PACKET_SIZE = 0
#         step = 0
#
#         with open('./defaults.json') as json_file:
#             default = json.load(json_file)
#             mask = default["mask"]
#             mask = []
#
#             PACKET_SIZE = default["PACKET_SIZE"]
#             step = default["step"]
#             step = 0
#
#             main_packet = default["main_packet"]
#             main_packet = 0
#
#             manual_index = default["manual_index"]
#
#         with open('./defaults.json', 'w') as outfile:
#             default["mask"] = mask
#             default["step"] = step
#             default["main_packet"] = main_packet
#             json.dump(default, outfile)
#
#
#         print("## POST Request sent to /visualizerurl. Now going to check for request data ")
#         print(request.files)
#         print("Printing the request to check for GENOME")
#         selected_genome = request.form['genomeVersion']
#         selected_genome_38 = False
#         if selected_genome == "Human GRCh38/hg38":
#             selected_genome_38 = True
#
#         # check if the post request has the file part
#         if 'igvfile' not in request.files:
#             print('No file part')
#             return redirect(request.url)
#
#         fileArray = []
#         for x in request.files:
#             fileArray.append(request.files[x])
#
#         print(fileArray)
#
#         if len(fileArray) == 0:
#             print('No selected file')
#             return redirect(request.url)
#
#         # We don't want to save the files... So none of the code below can be executed....
#         print("Here")
#         home = os.getcwd()
#         print(home)
#         tempdir = home + '/temp'
#         print(tempdir)
#         shutil.rmtree(tempdir)
#         os.mkdir('temp')
#
#         for file in fileArray:
#             if file.filename == '':
#                 print('No selected file')
#                 return redirect(request.url)
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 print(filename + "  IGV FILE :) :) ")
#                 file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#
#         print("## All files saved in the TEMP directory.")
#
#         mypath = tempdir + '/'
#
#         # 1. Load up the file from the temp folder.
#         onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
#         print(mypath + onlyfiles[0])
#
#         # New code that needs to be incorporated.
#         if onlyfiles[0].endswith('.csv'):
#             f = open(mypath + onlyfiles[0])
#             cols = f.readline().split(',')
#             data_full = pd.read_csv(mypath + onlyfiles[0], engine='python', names = cols)
#             data_full = data_full.reset_index(drop=True)
#         elif onlyfiles[0].endswith('.xlsx'):
#             data_full = pd.read_excel(mypath + onlyfiles[0],encoding=sys.getfilesystemencoding())
#             data_full = data_full.reset_index(drop=True)
#
#         data = data_full
#
#         # Now we have the BED file. Let's execute the python command .
#         print("Executing the python command now. ")
#         bed = './data/query.bed'
#
#         try:
#             x = pd.read_csv('./bamFilesFullPaths.txt', header=None)
#             length = len(x)
#         except:
#             length = -1;
#
#         tracks = []
#         for i in range(0, length):
#             tracks.append(x[0][i])
#
#         # GENOME VERSION 38
#
#         manual_index = 'X'
#         print(data['Chr'].values[0])
#         if('chr' in data['Chr'].values[0] or 'Chr' in data['Chr'].values[0]):
#             manual_index = 'chrX'
#
#         if selected_genome_38:
#             if (manual_index == 'X'):
#                 print("Trying to use index 1,2,3,....,X,Y,MT.")
#                 search = pd.concat([pd.DataFrame(data['Chr'].values), pd.DataFrame(data['Start'].values), pd.DataFrame(data['End'].values)], axis = 1).values.astype('U')
#                 search = pd.DataFrame(search)
#
#                 search = search.iloc[1:,:]
#                 search.columns = ['chrom', 'chromStart', 'chromEnd']
#                 search['chromStart'] = pd.to_numeric(search['chromStart'].values) - 2
#                 search.to_csv('./data/query.bed', index=None, header=False,sep='\t')
#                 print(search)
#
#                 main_packet = search
#
#                 with open('./defaults.json', 'w') as outfile:
#                     default["main_packet"] = json.loads(pd.DataFrame(main_packet).to_json(orient='split'))["data"]
#                     json.dump(default, outfile)
#
#                 fasta = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa"
#                 pass_arg = ['python3', './igvreports/test/igv_reports/report.py', bed, fasta, '--tracks'] + tracks + [ '--output', './static/igvjs_viewer.html']
#
#                 subprocess.check_call(pass_arg)
#
#             else:
#                 print("Manual index override. Trying to use index chr1,chr2,chr3,....,chrX,chrY,chrMT.")
#                 search = pd.concat([pd.DataFrame(data['Chr'].values), pd.DataFrame(data['Start'].values), pd.DataFrame(data['End'].values)], axis = 1).values.astype('U')
#                 search = pd.DataFrame(search)
#                 search = search.iloc[1:,:]
#                 search.columns = ['chrom', 'chromStart', 'chromEnd']
#                 search['chromStart'] = pd.to_numeric(search['chromStart'].values) - 2
#                 search.to_csv('./data/query.bed', index=None, header=False,sep='\t')
#                 main_packet = search
#
#                 with open('./defaults.json', 'w') as outfile:
#                     default["main_packet"] = json.loads(pd.DataFrame(main_packet).to_json(orient='split'))["data"]
#                     json.dump(default, outfile)
#
#                 fasta = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa"
#                 #indexURL = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa.fai"
#
#                 pass_arg = ['python3', './igvreports/test/igv_reports/report.py', bed, fasta, '--tracks'] + tracks + ['--output', './static/igvjs_viewer.html']
#                 subprocess.check_call(pass_arg)
#
#                 print("Success.")
#
#
#         ## GENOME VERSION 19
#         else:
#             if (manual_index == 'X'):
#                 print("Trying to use index 1,2,3,....,X,Y,MT.")
#                 search = pd.concat([pd.DataFrame(data['Chr'].values), pd.DataFrame(data['Start'].values), pd.DataFrame(data['End'].values)], axis = 1).values.astype('U')
#                 search = pd.DataFrame(search)
#
#                 search = search.iloc[1:,:]
#                 search.columns = ['chrom', 'chromStart', 'chromEnd']
#                 search['chromStart'] = pd.to_numeric(search['chromStart'].values) - 2
#                 search.to_csv('./data/query.bed', index=None, header=False,sep='\t')
#                 print(search)
#
#                 main_packet = search
#
#                 with open('./defaults.json', 'w') as outfile:
#                     default["main_packet"] = json.loads(pd.DataFrame(main_packet).to_json(orient='split'))["data"]
#                     json.dump(default, outfile)
#
#                 fasta =  'https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/1kg_v37/human_g1k_v37_decoy.fasta'
#                 pass_arg = ['python3', './igvreports/test/igv_reports/report.py', bed, fasta, '--tracks'] + tracks + [ '--output', './static/igvjs_viewer.html']
#
#                 subprocess.check_call(pass_arg)
#
#             else:
#                 print("Manual index override. Trying to use index chr1,chr2,chr3,....,chrX,chrY,chrMT.")
#                 search = pd.concat([pd.DataFrame(data['Chr'].values), pd.DataFrame(data['Start'].values), pd.DataFrame(data['End'].values)], axis = 1).values.astype('U')
#                 search = pd.DataFrame(search)
#                 search = search.iloc[1:,:]
#                 search.columns = ['chrom', 'chromStart', 'chromEnd']
#                 search['chromStart'] = pd.to_numeric(search['chromStart'].values) - 2
#                 search.to_csv('./data/query.bed', index=None, header=False,sep='\t')
#                 main_packet = search
#
#                 with open('./defaults.json', 'w') as outfile:
#                     default["main_packet"] = json.loads(pd.DataFrame(main_packet).to_json(orient='split'))["data"]
#                     json.dump(default, outfile)
#
#                 fasta = 'https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg19/hg19.fasta'
#                 pass_arg = ['python3', './igvreports/test/igv_reports/report.py', bed, fasta, '--tracks'] + tracks + ['--output', './static/igvjs_viewer.html']
#                 subprocess.check_call(pass_arg)
#
#         print("Done.")
#         print("Ajax call returns success here, and we change some HTML on the screen, through the JS")
#         return json.dumps({'len_file': len(search)})
#
#     with open('bamFilesFullPaths.txt', 'w') as f:
#         pass
#
#     with open('./defaults.json') as json_file:
#         default = json.load(json_file)
#
#     with open('./defaults.json', 'w') as outfile:
#         default["mask"] = []
#         json.dump(default, outfile)
#
#     # Reset the defaults.
#
#     return render_template('visualizer.html')

@app.route('/visualize', methods=['POST', 'GET'])
def my_visualizer_page():
    if request.method == 'POST':

        mask = 0
        PACKET_SIZE = 0
        step = 0

        with open('./defaults.json') as json_file:
            default = json.load(json_file)
            mask = default["mask"]
            mask = []

            PACKET_SIZE = default["PACKET_SIZE"]
            step = default["step"]
            step = 0

            main_packet = default["main_packet"]
            main_packet = 0

            manual_index = default["manual_index"]

        with open('./defaults.json', 'w') as outfile:
            default["mask"] = mask
            default["step"] = step
            default["main_packet"] = main_packet
            json.dump(default, outfile)


        print("## POST Request sent to /visualizerurl. Now going to check for request data ")
        # print(request.files)

        # print("Printing the request to check for GENOME")
        selected_genome = request.form['genomeVersion']
        selected_genome_38 = False
        if selected_genome == "Human GRCh38/hg38":
            selected_genome_38 = True

        # check if the post request has the file part
        if 'igvfile' not in request.files:
            print('No file part')
            return redirect(request.url)

        fileArray = []
        for x in request.files:
            fileArray.append(request.files[x])

        print(fileArray)

        if len(fileArray) == 0:
            print('No selected file')
            return redirect(request.url)

        # We don't want to save the files... So none of the code below can be executed....
        home = os.getcwd()
        print(home)
        tempdir = home + '/temp'
        print(tempdir)
        shutil.rmtree(tempdir)
        os.mkdir('temp')

        for file in fileArray:
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename + "  IGV FILE :) :) ")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        print("## All files saved in the TEMP directory.")

        mypath = tempdir + '/'

        # 1. Load up the file from the temp folder.
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        print(mypath + onlyfiles[0])

        # New code that needs to be incorporated.
        if onlyfiles[0].endswith('.csv'):
            f = open(mypath + onlyfiles[0])
            cols = f.readline().split(',')
            data_full = pd.read_csv(mypath + onlyfiles[0], engine='python', names = cols)
            data_full = data_full.reset_index(drop=True)
        elif onlyfiles[0].endswith('.xlsx'):
            data_full = pd.read_excel(mypath + onlyfiles[0],encoding=sys.getfilesystemencoding())
            data_full = data_full.reset_index(drop=True)

        data = data_full

        # Now we have the BED file. Let's execute the python command .
        print("Executing the python command now. ")
        bed = './data/query.bed'

        # try:
        #     x = pd.read_csv('./bamFilesFullPaths.txt', header=None)
        #     length = len(x)
        # except:
        #     length = -1;

        # Search for the files:
        tracks = []
        sandbox_path = '../../../webseq_sandbox/'
        list_of_tracks = request.form['trackfiles'].split(',')
        for filename in list_of_tracks:
            result = []
            for root, dir, files in os.walk(sandbox_path):
                if filename in files:
                    result.append(os.path.join(root, filename))
            print("We right here.")
            print(result)
            tracks.append(result[0])

        # GENOME VERSION 38

        manual_index = 'X'
        if('chr' in data['Chr'].values[0] or 'Chr' in data['Chr'].values[0]):
            manual_index = 'chrX'

        if selected_genome_38:
            if (manual_index == 'X'):
                print("Trying to use index 1,2,3,....,X,Y,MT.")
                search = pd.concat([pd.DataFrame(data['Chr'].values), pd.DataFrame(data['Start'].values), pd.DataFrame(data['End'].values)], axis = 1).values.astype('U')
                search = pd.DataFrame(search)

                search = search.iloc[1:,:]
                search.columns = ['chrom', 'chromStart', 'chromEnd']
                search['chromStart'] = pd.to_numeric(search['chromStart'].values) - 2
                search.to_csv('./data/query.bed', index=None, header=False,sep='\t')
                print(search)

                main_packet = search

                with open('./defaults.json', 'w') as outfile:
                    default["main_packet"] = json.loads(pd.DataFrame(main_packet).to_json(orient='split'))["data"]
                    json.dump(default, outfile)
                fasta = "./Datasets/hg38.fa"
                # fasta = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa"
                pass_arg = ['python3', './igvreports/test/igv_reports/report.py', bed, fasta, '--tracks'] + tracks + [ '--output', './static/igvjs_viewer.html']

                subprocess.check_call(pass_arg)

            else:
                print("Manual index override. Trying to use index chr1,chr2,chr3,....,chrX,chrY,chrMT.")
                search = pd.concat([pd.DataFrame(data['Chr'].values), pd.DataFrame(data['Start'].values), pd.DataFrame(data['End'].values)], axis = 1).values.astype('U')
                search = pd.DataFrame(search)
                search = search.iloc[1:,:]
                search.columns = ['chrom', 'chromStart', 'chromEnd']
                search['chromStart'] = pd.to_numeric(search['chromStart'].values) - 2
                search.to_csv('./data/query.bed', index=None, header=False,sep='\t')
                main_packet = search

                with open('./defaults.json', 'w') as outfile:
                    default["main_packet"] = json.loads(pd.DataFrame(main_packet).to_json(orient='split'))["data"]
                    json.dump(default, outfile)

                #fasta = "https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa"
                fasta = "./Datasets/hg38.fa"
                pass_arg = ['python3', './igvreports/test/igv_reports/report.py', bed, fasta, '--tracks'] + tracks + ['--output', './static/igvjs_viewer.html']
                subprocess.check_call(pass_arg)

                print("Success.")


        ## GENOME VERSION 19
        else:
            if (manual_index == 'X'):
                print("Trying to use index 1,2,3,....,X,Y,MT.")
                search = pd.concat([pd.DataFrame(data['Chr'].values), pd.DataFrame(data['Start'].values), pd.DataFrame(data['End'].values)], axis = 1).values.astype('U')
                search = pd.DataFrame(search)

                search = search.iloc[1:,:]
                search.columns = ['chrom', 'chromStart', 'chromEnd']
                search['chromStart'] = pd.to_numeric(search['chromStart'].values) - 2
                search.to_csv('./data/query.bed', index=None, header=False,sep='\t')
                print(search)

                main_packet = search

                with open('./defaults.json', 'w') as outfile:
                    default["main_packet"] = json.loads(pd.DataFrame(main_packet).to_json(orient='split'))["data"]
                    json.dump(default, outfile)

                #fasta =  'https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/1kg_v37/human_g1k_v37_decoy.fasta'
                fasta = "./Datasets/hg38.fa"
                pass_arg = ['python3', './igvreports/test/igv_reports/report.py', bed, fasta, '--tracks'] + tracks + [ '--output', './static/igvjs_viewer.html']

                subprocess.check_call(pass_arg)

            else:
                print("Manual index override. Trying to use index chr1,chr2,chr3,....,chrX,chrY,chrMT.")
                search = pd.concat([pd.DataFrame(data['Chr'].values), pd.DataFrame(data['Start'].values), pd.DataFrame(data['End'].values)], axis = 1).values.astype('U')
                search = pd.DataFrame(search)
                search = search.iloc[1:,:]
                search.columns = ['chrom', 'chromStart', 'chromEnd']
                search['chromStart'] = pd.to_numeric(search['chromStart'].values) - 2
                search.to_csv('./data/query.bed', index=None, header=False,sep='\t')
                main_packet = search

                with open('./defaults.json', 'w') as outfile:
                    default["main_packet"] = json.loads(pd.DataFrame(main_packet).to_json(orient='split'))["data"]
                    json.dump(default, outfile)

                #fasta = 'https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg19/hg19.fasta'
                fasta = "./Datasets/hg38.fa"
                pass_arg = ['python3', './igvreports/test/igv_reports/report.py', bed, fasta, '--tracks'] + tracks + ['--output', './static/igvjs_viewer.html']
                subprocess.check_call(pass_arg)

        print("Done.")
        print("Ajax call returns success here, and we change some HTML on the screen, through the JS")
        return json.dumps({'len_file': len(search)})

    with open('bamFilesFullPaths.txt', 'w') as f:
        pass

    with open('./defaults.json') as json_file:
        default = json.load(json_file)

    with open('./defaults.json', 'w') as outfile:
        default["mask"] = []
        json.dump(default, outfile)

    # Reset the defaults.

    return render_template('visualizer.html')

@app.route('/igvBatch', methods=['POST'])
def my_igvbatch_page():
    if request.method == 'POST':
        print("## POST Request sent to /igbatchurl. Now going to check for request data ")

        # We are going to get a mask in the request...
        # This is literally just a string...

        print("Here")
        home = os.getcwd()
        print(home)
        tempdir = home + '/temp'
        mypath = tempdir + '/'
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        mask = 0
        PACKET_SIZE = 0
        with open('./defaults.json') as json_file:
            default = json.load(json_file)
            mask = default["mask"]
            PACKET_SIZE = default["PACKET_SIZE"]
            step = default["step"]
            print(step)
            main_packet = default["main_packet"]

        print(mask)
        print(request.data)
        print(request.data.decode('UTF-8').split(','))
        mask += (request.data.decode('UTF-8').split(','))


        print(mask)
        # Need to dump this new mask back.

        with open('./defaults.json', 'w') as outfile:
            default["mask"] = mask
            step = step + 1
            default["step"] = step
            json.dump(default, outfile)

        # Ajax call returns success here, and we change some HTML on the screen, through the JS
        print("Ajax call returns success here, and we change some HTML on the screen, through the JS")
        # return json.dumps({'packet': packet, 'len_file': len(search)})
        return json.dumps({'len_file': 0})



###############################################################################
#####################        APP ROUTES    --- PLINK          ###################
###############################################################################
@app.route('/kinsex', methods=['POST', 'GET'])
def my_kinsex_task():
    if request.method == 'POST':
        print(request.form['x_check'])
        print(request.form['y_check'])

        bools = [request.form['x_check'], request.form['y_check']]

        format_type = request.form['format']

        print("## POST Request sent to /kin_sex_url. Now going to check for request data ")
        print(request.files)
        # check if the post request has the file part
        # if 'cleanfile' not in request.files:
        #     print('No file part')
        #     return redirect(request.url)
        fileArray = []
        for x in request.files:
            fileArray.append(request.files[x])

        #fileArray = request.files.getlist('cleanfile')
        print(fileArray)
        # if user does not select file, browser also
        # submit an empty part without filename

        if len(fileArray) == 0:
            print('No selected file')
            return redirect(request.url)

        print("Here")
        home = os.getcwd()
        print(home)
        tempdir = home + '/temp'
        print(tempdir)
        shutil.rmtree(tempdir)
        os.mkdir('temp')

        for file in fileArray:
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename + "  KIN_SEX ~~")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        print("## All files saved in the TEMP directory.")

        mypath = tempdir + '/'

        # 1. Load up all the files from the temp folder.
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        print(onlyfiles)

        ### : NEED TO EDIT!! WRITE A NEW METHOD THAT WILL ABSTRACT AWAY ALL THE KINSHIP AND SEX INFERENCE
        ### : FIRST, CHECK THE FILE SYSTEM WORKS OR NOT.s

        kin_sex_script(home, mypath, onlyfiles, bools, format_type)

        return redirect(request.url)

    # # GET REQUEST METHOD
    print("## GET Request sent to /kin_sexurl. Now redirecting to /")
    return render_template('/kin_sex.html')

@app.route('/ancestry', methods=['POST', 'GET'])
def my_ancestry_task():
    if request.method == 'POST':
        print(request.form)

        format_type = request.form['format']

        print("## POST Request sent to /ancestry_url. Now going to check for request data ")
        print(request.files)
        # check if the post request has the file part
        # if 'cleanfile' not in request.files:
        #     print('No file part')
        #     return redirect(request.url)
        fileArray = []
        for x in request.files:
            fileArray.append(request.files[x])

        #fileArray = request.files.getlist('cleanfile')
        print(fileArray)
        # if user does not select file, browser also
        # submit an empty part without filename

        if len(fileArray) == 0:
            print('No selected file')
            return redirect(request.url)

        print("Here")
        home = os.getcwd()
        print(home)
        tempdir = home + '/temp'
        print(tempdir)
        shutil.rmtree(tempdir)
        os.mkdir('temp')

        for file in fileArray:
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename + "  ANCESTRY ~~")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        print("## All files saved in the TEMP directory.")

        mypath = tempdir + '/'
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]


        ### COMMMENTED OUT FOR DEMO PURPOSES ONLY.  UNCOMMENTTTT
        task = ancestry_script.delay(home, mypath, onlyfiles, format_type)

        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}
    # # GET REQUEST METHOD
    print("## GET Request sent to /ancestry_url. Now redirecting to /")
    return render_template('/ancestry.html')

@app.route('/pca', methods=['POST', 'GET'])
def my_pca_task():
    if request.method == 'POST':

        with open('./defaults.json') as json_file:
            default = json.load(json_file)
            cdict = default["cdict"]
            key_dict = default["key_dict"]

        print("## POST Request sent to /pca_url. Now going to check for request data ")

        print(request.form)
        keys = list(request.form.keys())

        # 1000G has been selected.
        if request.form['db_name'] == "1000 Genomes Project":
            if keys[1] == 'all':
                print("Inside the all method. ")
                # Do the standard plot.
                df = pd.read_excel('./Datasets/20130606_sample_info.xlsx')

                q = df['Sample']
                r = df['Population']
                df = pd.concat([q,r], axis=1)

                pops = list(df['Population'].values)
                try:
                    eigenvecs = pd.read_csv('./temp/ancestry_buffer/merge3_pca.eigenvec', sep = ' ', header = -1)
                except:
                    return jsonify(-1)

                num_samples = list(eigenvecs[0]).index('HG00096')
                print("Number of samples is " + str(num_samples))

                sample = eigenvecs.iloc[:num_samples,:].iloc[:,1:]
                ref = pd.concat([eigenvecs.iloc[num_samples:,:][0], eigenvecs.iloc[num_samples:,:].iloc[:,2:]], axis= 1)
                ref.columns = list(range(0,ref.shape[1]))
                sample.columns = list(range(0, sample.shape[1]))

                mask = []
                for i in range(0,df.shape[0]):
                    mask.append(df['Sample'][i] in list(eigenvecs[0].values))

                df = df.loc[mask, :]
                df = df.reset_index(drop=True)

                PC1 = 1
                PC2 = 2

                data = []
                for g in np.unique(df['Population']):
                    ix = np.where(df['Population'] == g)
                    trace = go.Scatter(x=ref.iloc[ix[0],PC1], y=ref.iloc[ix[0],PC2],mode = 'markers', marker=dict(color = cdict[g]),name=g, text=key_dict[g])
                    data.append(trace)

                for j in range(0, sample.shape[0]):
                    sample_trace = go.Scatter(x = np.array(sample[PC1][j]), y = np.array(sample[PC2][j]), mode='markers',marker=dict(color = 'yellow', size = 7,line = dict(
                            width = 2,
                        )), name= sample[0][j], text=sample[0][j])
                    data.append(sample_trace)

                layout= go.Layout(
                    title= 'Population Inference: Reference + Study Samples',
                    hovermode= 'closest',
                    xaxis= dict(
                        title= 'PC ' + str(PC1),
                        ticklen= 5,
                        zeroline= False,
                        gridwidth= 2,
                    ),
                    yaxis=dict(
                        title= 'PC ' + str(PC2),
                        ticklen= 5,
                        gridwidth= 2,
                    ),
                )

                fig= go.Figure(data=data, layout=layout)


                plot_div = plot(fig, auto_open=False, filename="./static/temp-plot.html")
                plio.to_html(fig)

                # ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

                # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                # print(graphJSON)

                # iplot(fig)
                print("Now going to render template, watch out.")
                # return render_template('/ancestry.html', graphJSON=graphJSON)
                return plot_div

            else :
                # Here we need to parse through the populations, perform necessary extracts, and then remerge, do PCA, and plot.

                # Read through the option keys.
                pops = keys[1:]

                df = pd.read_excel('./Datasets/20130606_sample_info.xlsx')
                mask = []
                for i in range(0, df.shape[0]):
                    mask.append(df['Population'][i] in pops)

                include_these = pd.concat([ df[mask]['Family ID'], df[mask]['Sample']], axis=1)

                # count = 0
                # x = pd.read_csv('./Datasets/ancestry_data/chr1-X_extr_exclude.fam', sep = ' ', header = -1)[0]
                # for val in x:
                #     if val in include_these['Family ID'].values:
                #         count = count + 1
                np.savetxt('./data/filter_me.txt', include_these.values, fmt='%s')

                # Now we have the option keys saved, so we need to call a bash script that will do the PLINK part of the work. EXTRACT
                home = os.getcwd()
                mypath = home + '/temp' + '/'
                filenames = [f for f in listdir(mypath) if isfile(join(mypath, f))]
                arg = mypath + filenames[0].rsplit('.', 1)[0]

                pass_arg = ['./merge2.sh', arg]
                subprocess.check_call(pass_arg)

                ret = gen_pcs(1,2)

                if ret == -1:
                    return jsonify(-1)


                # Once that's done, then we will basically plot it in the same iframe, and the dropdowns will be there as well


                # Mark the check_bool global variable to be 1, so we know what kind of option has been turned on, and use the appropriate HTML file



                # Then make read the PCA file and make a plot inside.


        return redirect(request.url)

    # # GET REQUEST METHOD
    print("## GET Request sent to /ancestry. Now redirecting to /")
    return render_template('/ancestry.html')

@app.route('/refresh', methods=['POST'])
def refresh_my_pca():
    if request.method == 'POST':
        print("## POST Request sent to /refresh_url. Now going to check for request data ")
        data = request.get_json()

        PC1 = int(data['x'])
        PC2 = int(data['y'])
        ret = gen_pcs(PC1, PC2)
        return "{}"
    else:
        return "Invalid request"



###############################################################################
###############################################################################
#########################       PUSH FORWARD ROUTES       ####################
##############################################################################
###############################################################################


@app.route('/push', methods=['POST'])
def push_file():
    if request.method == 'POST':

        # If it is from FASTQ, cp the VCF files to temp/res/.
        # if request.form['url'] == "fastq":
        #     print("Executing MOVE VCF")
        #     pass_arg = ['./move_vcf_to_res.sh']
        #     subprocess.check_call(pass_arg)
        #

        print("Inside push.")

        # Call a shell script that does the following:
        # 1. Cleans files in the temp directory.
        # 2. Moves everythign from res to temp
        # 3. Cleans the res folder contents

        pass_arg = ['./push_modify.sh']
        subprocess.check_call(pass_arg)
        print("## All files saved in the TEMP directory.")

        # Then, here let's read the file names so we know what's in temp now
        home = os.getcwd()
        mypath = home + '/temp/'

        # 1. Load up all the files from the temp folder.
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        # Return this so we can display it.
        print(onlyfiles)

        # This is what we'll return.

        return json.dumps(onlyfiles)

    print("You're not supposed to be here.")
    return {}


###############################################################################
#########################       DOWNLOAD ROUTES       ##########################
###############################################################################
@app.route('/downloadgenepanel', methods=['POST'])
def download_genepanel_file():
    if request.method == 'POST':
        print('## POST request sent to /downloadgenepanel')

        home = os.getcwd()
        tempdir = home + '/temp/'
        mypath = tempdir + 'res/'

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        os.chdir(mypath)

        print(onlyfiles)

        response = []
        for file_name in onlyfiles:
            x = pd.read_csv(file_name)
            y = x.to_json(orient='records')
            response.append((file_name, y))


        print(response)
        os.chdir(home)

        final = jsonify(response)
        print("*********************************")
        print(final)
        print("*********************************")
        return final

@app.route('/downloadonevcf', methods=['POST','GET'])
def download_onevcf_file():
    if request.method == 'POST':
        print("## POST Request sent to /downloadonevcf.")

        # Change to the right directory.
        home = os.getcwd()
        tempdir = home + '/temp/'
        mypath = tempdir + 'res/'

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        # onlyfiles.append(mypath);

        print("ZIPPING NOW")
        pass_arg = ['./zipmeup.sh']
        subprocess.check_call(pass_arg)
        os.chdir(mypath)

        os.chdir(home)
        return send_file(mypath + 'annovar_results.zip' , mimetype='application/zip', as_attachment=True, attachment_filename='annovar_results.zip')
        # return jsonify(response)
    else:
        print("## POST Request sent to /downloadonevcf.")

        # Change to the right directory.
        home = os.getcwd()
        tempdir = home + '/temp/'
        mypath = tempdir + 'res/'

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        # onlyfiles.append(mypath);

        print("ZIPPING NOW")
        pass_arg = ['./zipmeup.sh']
        subprocess.check_call(pass_arg)
        os.chdir(home)
        return send_file(mypath + 'annovar_results.zip' , mimetype='application/zip', as_attachment=True, attachment_filename='annovar_results.zip')


@app.route('/downloadtwovcf', methods=['POST'])
def download_twovcf_file():
    if request.method == 'POST':
        print("## POST Request sent to /downloadtwovcf.")

        # Change to the right directory.
        home = os.getcwd()
        tempdir = home + '/temp/'
        mypath = tempdir + 'res/'

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        # onlyfiles.append(mypath);

        os.chdir(mypath)

        response = []
        for file_name in onlyfiles:
            try:
                x = pd.read_csv(file_name)
            except:
                continue
            y = x.to_json(orient='records')
            response.append((file_name, y))

        os.chdir(home)

        # return send_file(mypatsh + 'cleanedFiles.zip', as_attachment=True, mimetype='application/zip')
        return jsonify(response)


@app.route('/downloadclean', methods=['POST'])
def download_clean_file():
    if request.method == 'POST':
        print("## POST Request sent to /downloadclean.")

        # Change to the right directory.
        home = os.getcwd()
        tempdir = home + '/temp/'
        mypath = tempdir + 'res/'

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        # onlyfiles.append(mypath);

        os.chdir(mypath)

        # file = open('cleanedFiles.zip', 'wb+')
        # zipf = zipfile.ZipFile(file, "w")

        response = []
        for file_name in onlyfiles:
            x = pd.read_csv(file_name)
            y = x.to_json(orient='records')
            response.append((file_name, y))

        os.chdir(home)

        return jsonify(response)


@app.route('/downloadannotate', methods=['POST'])
def download_annotate_file():
    if request.method == 'POST':
        print("## POST Request sent to /downloadannoate.")

        # Change to the right directory.
        home = os.getcwd()
        tempdir = home + '/temp/'
        mypath = tempdir + 'res/'

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        os.chdir(mypath)
        response = []
        for file_name in onlyfiles:

            x = pd.read_csv(file_name)
            y = x.to_json(orient='records')
            response.append((file_name, y))

        os.chdir(home)

        print("reached here")

        return jsonify(response)


@app.route('/downloadfilter', methods=['POST'])
def download_filter_file():
    if request.method == 'POST':
        print("## POST Request sent to /downloadfilter.")

        # Change to the right directory.
        home = os.getcwd()
        tempdir = home + '/temp/'
        mypath = tempdir + 'res/'

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        os.chdir(mypath)

        response = []
        for file_name in onlyfiles:
            # print("Fileeee:")
            # print(file_name)
            #zipf.write(str(mypath + file_name), arcname= 'cleanData/' + file_name)
            x = pd.read_csv(file_name)
            y = x.to_json(orient='records')
            response.append((file_name, y))

        os.chdir(home)

        print("reached here")

        return jsonify(response)


@app.route('/downloadmodes', methods=['POST'])
def download_modes_file():
    if request.method == 'POST':
        print("## POST Request sent to /downloadmodes.")

        # Change to the right directory.
        home = os.getcwd()
        tempdir = home + '/temp/'
        mypath = tempdir + 'res/'

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        # onlyfiles.append(mypath);

        os.chdir(mypath)

        # file = open('cleanedFiles.zip', 'wb+')
        # zipf = zipfile.ZipFile(file, "w")

        response = []
        for file_name in onlyfiles:
            # print("Fileeee:")
            # print(file_name)
            #zipf.write(str(mypath + file_name), arcname= 'cleanData/' + file_name)
            x = pd.read_csv(file_name)
            y = x.to_json(orient='records')
            response.append((file_name, y))
        # print(response)
            #response.append((file_name, open(file_name, "r+"), 'text/csv'))
        # zipf.close()
        # file.seek(0)
        os.chdir(home)

        # return send_file(mypath + 'cleanedFiles.zip', as_attachment=True, mimetype='application/zip')
        return jsonify(response)


@app.route('/downloadunbiasedcohort', methods=['POST'])
def download_unbiasedcohort_file():
    if request.method == 'POST':
        print("## POST Request sent to /download_unbiasedcohort.")

        # Change to the right directory.
        home = os.getcwd()
        tempdir = home + '/temp/'
        mypath = tempdir + 'res/'

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        # onlyfiles.append(mypath);

        os.chdir(mypath)

        # file = open('cleanedFiles.zip', 'wb+')
        # zipf = zipfile.ZipFile(file, "w")

        response = []
        for file_name in onlyfiles:
            # print("Fileeee:")
            # print(file_name)
            #zipf.write(str(mypath + file_name), arcname= 'cleanData/' + file_name)
            x = pd.read_csv(file_name)
            y = x.to_json(orient='records')
            response.append((file_name, y))
        # print(response)
            #response.append((file_name, open(file_name, "r+"), 'text/csv'))
        # zipf.close()
        # file.seek(0)
        os.chdir(home)

        # return send_file(mypath + 'cleanedFiles.zip', as_attachment=True, mimetype='application/zip')
        return jsonify(response)


@app.route('/downloadbiasedcohort', methods=['POST'])
def download_biasedcohort_file():
    if request.method == 'POST':
        print("## POST Request sent to /download_biasedcohort.")

        # Change to the right directory.
        home = os.getcwd()
        tempdir = home + '/temp/'
        mypath = tempdir + 'res/'

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        # onlyfiles.append(mypath);

        os.chdir(mypath)

        # file = open('cleanedFiles.zip', 'wb+')
        # zipf = zipfile.ZipFile(file, "w")

        response = []
        for file_name in onlyfiles:
            # print("Fileeee:")
            # print(file_name)
            #zipf.write(str(mypath + file_name), arcname= 'cleanData/' + file_name)
            x = pd.read_csv(file_name)
            y = x.to_json(orient='records')
            response.append((file_name, y))
        # print(response)
            #response.append((file_name, open(file_name, "r+"), 'text/csv'))
        # zipf.close()
        # file.seek(0)
        os.chdir(home)

        # return send_file(mypath + 'cleanedFiles.zip', as_attachment=True, mimetype='application/zip')
        return jsonify(response)

@app.route('/downloadgen_blacklist', methods=['POST'])
def download_gen_blacklist_ile():
    if request.method == 'POST':
        print("## POST Request sent to /download_gen_blacklist.")

        # Change to the right directory.
        home = os.getcwd()
        tempdir = home + '/temp/'
        mypath = tempdir + 'res/'

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        # onlyfiles.append(mypath);

        os.chdir(mypath)

        # file = open('cleanedFiles.zip', 'wb+')
        # zipf = zipfile.ZipFile(file, "w")

        response = []
        for file_name in onlyfiles:
            # print("Fileeee:")
            # print(file_name)
            #zipf.write(str(mypath + file_name), arcname= 'cleanData/' + file_name)
            x = pd.read_csv(file_name)
            y = x.to_json(orient='records')
            response.append((file_name, y))
        # print(response)
            #response.append((file_name, open(file_name, "r+"), 'text/csv'))
        # zipf.close()
        # file.seek(0)
        os.chdir(home)

        # return send_file(mypath + 'cleanedFiles.zip', as_attachment=True, mimetype='application/zip')
        return jsonify(response)

@app.route('/downloadapply_blacklist', methods=['POST'])
def download_apply_blacklist_ile():
    if request.method == 'POST':
        print("## POST Request sent to /download_apply_blacklist.")

        # Change to the right directory.
        home = os.getcwd()
        tempdir = home + '/temp/'
        mypath = tempdir + 'res/'

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        # onlyfiles.append(mypath);
        # ix = onlyfiles.index('README.txt')
        # README = onlyfiles[ix]
        # onlyfiles.pop(ix)

        os.chdir(mypath)

        # file = open('cleanedFiles.zip', 'wb+')
        # zipf = zipfile.ZipFile(file, "w")

        response = []
        for file_name in onlyfiles:
            # print("Fileeee:")
            # print(file_name)
            #zipf.write(str(mypath + file_name), arcname= 'cleanData/' + file_name)
            x = pd.read_csv(file_name)
            y = x.to_json(orient='records')
            response.append((file_name, y))

        # print(response)
            #response.append((file_name, open(file_name, "r+"), 'text/csv'))
        # zipf.close()
        # file.seek(0)
        os.chdir(home)

        # return send_file(mypath + 'cleanedFiles.zip', as_attachment=True, mimetype='application/zip')
        return jsonify(response)


@app.route('/downloadkinsex', methods=['POST'])
def download_kinsex_file():
    if request.method == 'POST':
        print("## POST Request sent to /download_kinsex.")

        # Change to the right directory.
        home = os.getcwd()
        tempdir = home + '/temp/'
        mypath = tempdir + 'res/'

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        # onlyfiles.append(mypath);

        os.chdir(mypath)

        # file = open('cleanedFiles.zip', 'wb+')
        # zipf = zipfile.ZipFile(file, "w")

        response = []
        for file_name in onlyfiles:
            x = pd.read_csv(file_name)
            y = x.to_json(orient='records')
            response.append((file_name, y))

        os.chdir(home)

        # return send_file(mypatsh + 'cleanedFiles.zip', as_attachment=True, mimetype='application/zip')
        return jsonify(response)


@app.route('/downloadIGV', methods=['POST'])
def download_igv_file():
    if request.method == 'POST':
        print("## POST Request sent to /download_igv.")

        # Change to the right directory.
        home = os.getcwd()
        tempdir = home + '/temp/'
        mypath = tempdir + 'res/'

        onlyfiles = [f for f in listdir(tempdir) if isfile(join(tempdir, f))]
        file = onlyfiles[0]

        # Need to format it so we incorporate the mask in it as well.
        if file.endswith('.csv'):
            f = open(tempdir + file)
            # cols = f.readline().split(',')
            x = pd.read_csv(tempdir + file, engine='python', header = 0)
            x = x.reset_index(drop=True)
            file_name = file.split('.csv')[0] + '_IGV.csv'

        elif file.endswith('.xlsx'):
            x = pd.read_excel(tempdir + file,encoding=sys.getfilesystemencoding())
            x = x.reset_index(drop=True)
            file_name = file.split('.xlsx')[0] + '_IGV.csv'

        mask = 0
        with open('./defaults.json') as json_file:
            default = json.load(json_file)
            mask = default["mask"]
        y = pd.concat([pd.DataFrame(x.iloc[:,:list(x.columns).index('Alt') + 1]), pd.DataFrame(mask, columns=['IGV']) ,pd.DataFrame(x.iloc[:,list(x.columns).index('Alt') + 1:])], axis = 1)

        print(y)
        response = []

        # Then also need to give it the right file name.
        print(file_name)
        z = y.to_json(orient='records')
        response.append((file_name, z))
        return jsonify(response)


@app.route('/selecttrack' , methods = ['POST'])
def select_track():
    if request.method == 'POST':

        # Here, trigger the Tkinter UI menu, and save the names of the files....
        pass_arg = ['python3', 'tkin.py']
        subprocess.check_call(pass_arg)

        try:
            x = pd.read_csv('./bamFilesFullPaths.txt', header=None)
            length = len(x)
        except:
            length = -1;

        # Tracks must be the relative/full path of the BAM files.
        tracks = []

        for i in range(0, length):
            tracks.append(x[0][i])

        return jsonify({"data": tracks ,"status": "OK"})
    else:
        return {}

###############################################################################
###############################################################################

# !!!!!!!!!!!!!!!!!!!!!!!!
# CORE FUNCTIONS FOR TASKS
# !!!!!!!!!!!!!!!!!!!!!!!!

# Cleaning and Prefiltering. Actual Scripts for Processing.

@celery.task(bind=True)
def wes_cleaning(self, home, mypath, filenames, include):

    print("## Celery Task WES_CLEANING called.")
    remove = []
    include = include.split(',')

    if (include[0] == 'false'):
        print("Exonic unchecked. ")
        remove.append('exonic')
        remove.append('exonic;splicing')

    if (include[1] == 'false'):
        remove.append('ncRNA_exonic')
        remove.append('ncRNA_exonic;splicing')

    if (include[2] == 'false'):
        remove.append('splicing')
        remove.append('ncRNA_exonic;splicing')

    if (include[3] == 'false'):
        remove.append('ncRNA_splicing')

    if (include[4] == 'false'):
        remove.append('intronic')

    if (include[5] == 'false'):
        remove.append('ncRNA_intronic')

    if (include[6] == 'false'):
        remove.append('intergenic')

    if (include[7] == 'false'):
        remove.append('downstream')
        remove.append('upstream;downstream')

    if (include[8] == 'false'):
        remove.append('upstream')
        remove.append('upstream;downstream')

    if (include[9] == 'false'):
        remove.append('UTR3')
        remove.append('UTR5;UTR3')
        remove.append('UTR3;UTR5')

    if (include[10] == 'false'):
        remove.append('UTR5')
        remove.append('UTR5;UTR3')
        remove.append('UTR3;UTR5')
    remove_filter = remove


    print(remove)

    os.chdir(mypath)
    # Retrieve rough number of columns. This is a little repetitive since we
    # are going to read this dataframe again, but it is required to have an
    # accurate estimate of how long it'll take for our progressbar, and when
    # we should update the bar.
    if filenames[0].endswith('.csv'):
        t = pd.read_csv(filenames[0])
        t = t.reset_index(drop=True)
    elif filenames[0].endswith('.xlsx'):
        t = pd.read_excel(filenames[0])
        t = t.reset_index(drop=True)

    # total: Number of iterations needed across all files.
    # i: our iterate.
    total = len(filenames) * len(t.columns)
    print(total)
    perc = 0
    i = 0

    # 1. Read files as dataframes.
    wANNOVAR_data_list = []
    for file in filenames:
        if file.endswith('.csv'):
            x = pd.read_csv(file)
            x = x.reset_index(drop=True)

        elif file.endswith('.xlsx'):
            x = pd.read_excel(file)
            x = x.reset_index(drop=True)

        wANNOVAR_data_list.append(x)

    perc = perc + 5

    print("About to update now. ")
    self.update_state(state='PROGRESS', meta={'current': perc, 'total': 100, 'status': 'Read all your files'})

    remove = ['GeneDetail.refGene', '1000G_AFR', '1000G_AMR', '1000G_EAS', '1000G_EUR', '1000G_SAS', 'ExAC_AFR',
              'ExAC_AMR', 'ExAC_EAS', 'ExAC_FIN', 'ExAC_NFE', 'ExAC_OTH', 'ExAC_SAS', 'ESP6500si_ALL', 'ESP6500si_AA',
              'ESP6500si_EA', 'CG46', 'NCI60', 'ClinVar_SIG', 'ClinVar_DIS', 'ClinVar_ID', 'ClinVar_DB', 'ClinVar_DBID',
              'GWAS_DIS', 'GWAS_OR', 'GWAS_BETA', 'GWAS_PUBMED', 'GWAS_SNP', 'GWAS_P', 'SIFT_converted_rankscore',
              'Polyphen2_HDIV_rankscore', 'Polyphen2_HVAR_rankscore', 'LRT_score', 'LRT_converted_rankscore', 'LRT_pred', 'MutationTaster_converted_rankscore',
              'MutationAssessor_score', 'MutationAssessor_score_rankscore', 'MutationAssessor_pred', 'FATHMM_score',
              'FATHMM_converted_rankscore', 'FATHMM_pred', 'PROVEAN_converted_rankscore', 'VEST3_score', 'VEST3_rankscore',
              'MetaSVM_score', 'MetaSVM_rankscore', 'MetaSVM_pred', 'MetaLR_score', 'MetaLR_rankscore', 'MetaLR_pred',
              'MetaSVM_rankscore', 'MetaSVM_pred', 'MetaLR_score', 'MetaLR_rankscore', 'MetaLR_pred', 'M-CAP_score',
              'M-CAP_rankscore', 'M-CAP_pred', 'CADD_raw', 'CADD_raw_rankscore', 'DANN_score', 'DANN_rankscore', 'fathmm-MKL_coding_score',
              'fathmm-MKL_coding_rankscore', 'fathmm-MKL_coding_pred', 'Eigen_coding_or_noncoding', 'Eigen-raw', 'Eigen-PC-raw',
              'GenoCanyon_score', 'GenoCanyon_score_rankscore', 'integrated_fitCons_score', 'integrated_fitCons_score_rankscore',
              'integrated_confidence_value', 'GERP++_RS', 'GERP++_RS_rankscore', 'phyloP100way_vertebrate', 'phyloP100way_vertebrate_rankscore',
              'phyloP20way_mammalian', 'phyloP20way_mammalian_rankscore', 'phastCons100way_vertebrate', 'phastCons100way_vertebrate_rankscore',
              'phastCons20way_mammalian', 'phastCons20way_mammalian_rankscore', 'SiPhy_29way_logOdds', 'SiPhy_29way_logOdds_rankscore',
              'Interpro_domain', 'GTEx_V6_gene', 'GTEx_V6_tissue', 'Otherinfo.1', 'Otherinfo.2', 'Otherinfo.3', 'Otherinfo.4',
              'Otherinfo.5', 'Otherinfo.6', 'Otherinfo.7', 'Otherinfo.8', 'Otherinfo.9', 'Otherinfo.10', 'Otherinfo.11', 'Otherinfo.12']

    wANNOVAR_data_cleaned_list = []
    for wANNOVAR_data in wANNOVAR_data_list:
        wANNOVAR_data_cleaned = pd.DataFrame()
        for column_name in wANNOVAR_data.columns:
            if column_name == 'Otherinfo':
                # This is being outputted as zygo, check Nikhil's files-- if they are current.
                new_column = 'zygosity'
            else:
                new_column = column_name
            if column_name not in remove:
                wANNOVAR_data_cleaned[new_column] = wANNOVAR_data[column_name]
            i = i + 1
            print(i)
            print(45/total)
            print(i*(45/total))
            print(perc)
            print(perc + i*(45/total))
            self.update_state(state='PROGRESS', meta={'current': perc + i*(20/total), 'total': 100, 'status': 'Cleaning up your files'});

        wANNOVAR_data_cleaned_list.append(wANNOVAR_data_cleaned)

    # Done with half of the analyses.
    j = 25;

    print("Finished cleaning, now creating directory structure.")
    # Make a results directory
    if os.path.exists('res') == False:
        os.mkdir('res')

    # wANNOVAR cleaned list contains clean dataframes. So we're going to prefilter them as well
    # in this step. And, then output everything in one go.

    print("Going to start the prefiltering process right now.")
    wANNOVAR_data_prefiltered_list = []
    N = len(filenames)
    which = 0

    for input_data in wANNOVAR_data_cleaned_list:
        COL_NAMES = input_data.columns
        # remove_filter = ['intronic', 'intergenic', 'ncRNA_intronic',
        #                  'downstream', 'upstream', 'upstream;downstream', 'UTR3', 'UTR5']

        output_data = pd.DataFrame(columns=COL_NAMES)

        num_rows = input_data.shape[0]

        # Goes through all the rows
        num = 0
        for i in range(0, num_rows):
            print(i)
            if input_data['Func.refGene'][i] not in remove_filter:
                if input_data['Func.refGene'][i] == 'exonic':
                    if input_data['ExonicFunc.refGene'][i] != 'synonymous SNV':
                        output_data = output_data.append(input_data.iloc[i])
    # =============================================================================
    #                     print(input_data['Func.refGene'][i],input_data['ExonicFunc.refGene'][i])
    # =============================================================================
                else:
                    output_data = output_data.append(input_data.iloc[i])
            num = num + 1
            where = 25 + which*(70/N) + num*(70/(N*num_rows))
            print(where)
            self.update_state(state='PROGRESS', meta={'current':where , 'total': 100, 'status': 'Prefiltering your files'})

        try:
            output_data = output_data.drop(['Unnamed: 0.1'], axis=1)
            output_data = output_data.drop(['Unnamed: 0'], axis=1)
        except Exception as e:
            print(e)
        finally:
            output_data.index = range(0, output_data.shape[0])

        y = output_data

        which = which + 1
        self.update_state(state='PROGRESS', meta={'current': j + 70/N, 'total': 100, 'status': 'Prefiltering your files'})
        wANNOVAR_data_prefiltered_list.append(y)

    k = 0
    for y in wANNOVAR_data_prefiltered_list:
        try:
            chr_ix = list(y.columns).index("Chr")

        except ValueError:
            try:
                chr_ix = list(y.columns).index("chr")
            except ValueError:
                chr_ix = 0;

        y = y.iloc[:, chr_ix:]
        # Write the result dataframe into that directory
        y.to_csv('res/' + filenames[k].rsplit('.', 1)[0] + '_prefilter.csv', index = None)
        k = k + 1

    self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Cleaning up your files'})
    os.chdir(home)

    return {'current':100, 'total':100, 'status': 'Task Completed!', 'result': 100}

def prefilter_frame(self, input_data, N, which ):
    # Giving the method a whole dataframe
    # Column headers for the input file
    COL_NAMES = input_data.columns
    remove_filter = ['intronic', 'intergenic', 'ncRNA_intronic',
                     'downstream', 'upstream', 'upstream;downstream', 'UTR3', 'UTR5']

    # Creates a new empty dataframe with the same column headers that will contain prefiltered data
    output_data = pd.DataFrame(columns=COL_NAMES)

    num_rows = input_data.shape[0]

    # Goes through all the rows
    num = 0
    for i in range(0, num_rows):

        print(i)
        if input_data['Func.refGene'][i] not in remove_filter:
            if input_data['Func.refGene'][i] == 'exonic':
                if input_data['ExonicFunc.refGene'][i] != 'synonymous SNV':
                    output_data = output_data.append(input_data.iloc[i])
# =============================================================================
#                     print(input_data['Func.refGene'][i],input_data['ExonicFunc.refGene'][i])
# =============================================================================
            else:
                output_data = output_data.append(input_data.iloc[i])
        num = num + 1
        where = 25 + which*(70/N) + num*(70/(N*num_rows))
        print(where)
        self.update_state(state='PROGRESS', meta={'current':where , 'total': 100, 'status': 'Prefiltering your files'})

    try:
        output_data = output_data.drop(['Unnamed: 0.1'], axis=1)
    except Exception as e:
        print(e)
    finally:
        output_data.index = range(0, output_data.shape[0])
        return output_data

# Annotations
def MSC_func(self, num_genes, refdict, gene, length, which ):
    MSC_values = []
    msc_width = (90/length)/5
    iterate = msc_width/num_genes

    for i in range(num_genes):  # for all the genes that we are looking at in this file
        if refdict.get(gene[i], 'NaN') != 'NaN':  # if the dictionary contains the gene
            # add the corresponding MSC value to a list
            MSC_values.append(refdict[gene[i]])
        else:
            MSC_values.append('NaN')  # otherwise add this filler

        self.update_state(state='PROGRESS', meta={'current': 5 + (which)*90/length + i*iterate, 'total': 100, 'status': ' Annotating files with MSC.'})

    return MSC_values

def pData_func(self, num_genes, refdict, gene, length, which):

    iterate = ((90/length)/5)/num_genes
    msc_width = (90/length)/5

    pLI_matched = []
    pRec_matched = []
    pNull_matched = []
    for i in range(num_genes):
        if refdict.get(gene[i], 'NaN') != 'NaN':
            pLI_matched.append(refdict[gene[i]][0])
            pRec_matched.append(refdict[gene[i]][1])
            pNull_matched.append(refdict[gene[i]][2])
        else:
            pLI_matched.append('NaN')  # otherwise add this filler
            pRec_matched.append('NaN')  # otherwise add this filler
            pNull_matched.append('NaN')  # otherwise add this filler

        self.update_state(state='PROGRESS', meta={'current': 5 + (which)*90/length + msc_width +  i*iterate, 'total': 100, 'status': ' Annotating files with pLI, pRec, pNull.'})

    return pLI_matched, pRec_matched, pNull_matched

def GDI_func(self, num_genes, refdict, gene, length, which):

    iterate = ((90/length)/5)/num_genes
    pli_msc_width = (2*(90/length))/5

    GDI_matched = []
    GDI_Phred_matched = []
    for i in range(num_genes):
        if refdict.get(gene[i], 'NaN') != 'NaN':
            GDI_matched.append(refdict[gene[i]][0])
            GDI_Phred_matched.append(refdict[gene[i]][1])
        else:
            GDI_matched.append('NaN')  # otherwise add this filler
            GDI_Phred_matched.append('NaN')  # otherwise add this filler
        self.update_state(state='PROGRESS', meta={'current': 5 + (which)*90/length + pli_msc_width + i*iterate, 'total': 100, 'status': ' Annotating files with GDI.'})

    return GDI_matched, GDI_Phred_matched

def split_delim(genedict, x, delimiter):
    y = x.split(';')
    genestring = ''
    for gene in y:
        genestring += (genedict[gene] +';')
    genestring = genestring[:-1]
    return genestring

def previous(genes, key):
    for i in range(0, genes.shape[0]):
        x = str(genes.loc[i ,'Previous symbols'])
        if x != 'nan':
            if (key in [y.strip() for y in x.split(',')]) == True:
                return i
    return -1

def synonym(genes, key):
    for i in range(0, genes.shape[0]):
        x = str(genes.loc[i ,'Synonyms'])
        if x != 'nan':
            if (key in [y.strip() for y in x.split(',')]  ) == True:
                return i
    return -1

def annotate_gene(genedict, genes, gene):

    # Check if its a nan
    try:
        if np.isnan(gene):
            return ''
    except:
        pass

    # Check if there's ; in gene name
    if ';' in gene:
        gene_list = gene.split(';')
        string = ''
        for x in gene_list:
            string += (str(annotate_gene(genedict, genes, x)) + ';')
        return string

    if ',' in gene:
        gene_list = gene.split(';')
        string = ''
        for x in gene_list:
            string += (str(annotate_gene(genedict, genes, x)) + ';')
        return string

    # The actual gene
    try:
        x = genedict[gene]
        # If found
        if str(x) != 'None':
            return x
        else:
            # There might be an older name
            try:
                ix = previous(genes, gene)
                if ix != -1:
                        return genes.iloc[ix, :]['Approved symbol'] + ': '
                        + annotate_gene(genedict, genes, genes.iloc[ix, :]['Approved symbol'])

            except:
                pass;

            # There might be a synonym
            try:
                ix = synonym(genes, gene)
                if ix != -1:
                        return genes.iloc[ix, :]['Approved symbol'] + ': '
                        + annotate_gene(genedict, genes, genes.iloc[ix, :]['Approved symbol'])
            except:
                pass

    except:
        pass;

    # There might be an older name
    try:
        ix = previous(genes, gene)
        if ix != -1:
                return genes.iloc[ix, :]['Approved symbol'] + ': '
                + annotate_gene(genedict, genes, genes.iloc[ix, :]['Approved symbol'])

    except:
        pass;

    # There might be a synonym
    try:
        ix = synonym(genes, gene)
        if ix != -1:
                y = genes.iloc[ix, :]['Approved symbol']
                return y + ': ' + annotate_gene(genedict, genes,y)
    except:
        pass



def CDG_func(self, num_genes, chkg, cokg, chrdict, cordict, gene, length, which):

    CDG_HGMD_KNOWN = []
    CDG_OMIM_KNOWN = []
    CDG_HGMD_ROUTE = []
    CDG_OMIM_ROUTE = []

    iterate = (2*(90/length)/5)/num_genes
    gdi_pli_msc_width = (3*(90/length))/5

    for i in range(num_genes):  # for all the genes that we are looking at in this file
        if gene[i] in list(chkg):
            # add the corresponding value to a list
            CDG_HGMD_KNOWN.append('yes')
            CDG_HGMD_ROUTE.append(" ")
        else:
            CDG_HGMD_KNOWN.append('no')
            if chrdict.get(gene[i], 'NaN') != 'NaN':
                CDG_HGMD_ROUTE.append(chrdict[gene[i]])
            else:
                CDG_HGMD_ROUTE.append('No data')

        if gene[i] in list(cokg):
            # add the corresponding value to a list
            CDG_OMIM_KNOWN.append('yes')
            CDG_OMIM_ROUTE.append(" ")
        else:
            CDG_OMIM_KNOWN.append('no')
            if cordict.get(gene[i], 'NaN') != 'NaN':
                CDG_OMIM_ROUTE.append(cordict[gene[i]])
            else:
                CDG_OMIM_ROUTE.append('No data')

        self.update_state(state='PROGRESS', meta={'current': 5 + (which)*90/length + gdi_pli_msc_width + i*iterate, 'total': 100, 'status': ' Annotating files with CDG Data.'})

    return CDG_HGMD_KNOWN, CDG_OMIM_KNOWN, CDG_HGMD_ROUTE, CDG_OMIM_ROUTE

def annotate(self, input_data, home, length, which):

    # Mutation Significance Cutoff
    MSC_all_data = pd.read_excel(
        home + '/Datasets/MSC data.xlsx', header=None)  # read the MSC data file
    Genes = MSC_all_data.loc[:, 0]  # store the gene names
    # store the MSC values that correspond to above gene names
    MSCs = MSC_all_data.loc[:, 8]
    tot_mgenes = len(MSC_all_data)  # get length of column
    MSC_dict = {}  # empty dictionary

    for i in range(tot_mgenes):
        # each pair of the dictionary is gene name:Msc value
        MSC_dict[Genes[i]] = MSCs[i]

    num_genes = len(input_data)
    gene = input_data['Gene.refGene']
    output_data = pd.DataFrame.copy(input_data)
    print("MSC Access")
    MSC_values = MSC_func(self, num_genes, MSC_dict, gene, length, which)

    j = 5 + (which)*90/length + (90/length)/5
    self.update_state(state='PROGRESS', meta={'current': j, 'total': 100, 'status': 'Completed MSC Annotations.'});


    #####Loading pLI data into memory#####
    pdata = pd.read_csv(home + '/Datasets/pli_data.txt', sep="\t", header=None)
    pLI = pdata.loc[:, 19]
    pRec = pdata.loc[:, 20]
    pNull = pdata.loc[:, 21]
    pgenes = pdata.loc[:, 1]
    tot_pgenes = len(pdata)
    pdict = {}

    for i in range(tot_pgenes):
        pdict[pgenes[i]] = [pLI[i], pRec[i], pNull[i]]

    print("pLI Access")
    pLI_matched, pRec_matched, pNull_matched = pData_func(self, num_genes, pdict, gene, length, which)


    j = 5 + (which)*90/length + 2*(90/length)/5
    self.update_state(state='PROGRESS', meta={'current': j, 'total': 100, 'status': 'Completed pLi, pRec, pNull Annotations.'});


    #####Loading GDI into memory#####
    gdi_data = pd.read_csv(
        home + '/Datasets/GDI_full.txt', sep="\t", header=None)
    GDI = gdi_data.loc[:, 1]
    GDI_Phred = gdi_data.loc[:, 2]
    ggenes = gdi_data.loc[:, 0]

    # a dictionary containing all human genes, with their GDI values (raw and Phred)
    metrics_dictionary = {}
    tot_mgenes = len(gdi_data)

    for i in range(tot_mgenes):
        metrics_dictionary[ggenes[i]] = [GDI[i], GDI_Phred[i]]

    print("GDI Access")
    GDI_matched, GDI_Phred_matched = GDI_func(self, num_genes, metrics_dictionary, gene, length, which)
    print("Executed GDI Statement.")

    j = 5 + (which)*90/length + 3*(90/length)/5
    self.update_state(state='PROGRESS', meta={'current': j, 'total': 100, 'status': 'Completed GDI Annotations.'});

    #####Loading CDG into memory#####
    CDG_HGMD_PREDICTED = pd.read_excel(
        home + "/Datasets/CDG_full_public_HPO.xlsx")  # read the data file
    j = 5 + (which)*90/length + 4*(90/length)/5 + 2*(90/length)/10
    self.update_state(state='PROGRESS', meta={'current': j, 'total': 100, 'status': 'Read the CDG data file.'});


    CDG_HGMD_KNOWN = pd.read_excel(home + "/Datasets/HGMD_known.xlsx")
    # j = 5 + (which)*90/length + 4*(90/length)/5 + 4*(90/length)/10
    self.update_state(state='PROGRESS', meta={'current': j, 'total': 100, 'status': 'Read the HGMD data file.'});

    CDG_OMIM_PREDICTED = pd.read_excel(home + "/Datasets/CDG_predicted.xlsx")
    j = 5 + (which)*90/length + 4*(90/length)/5 + 6*(90/length)/10
    self.update_state(state='PROGRESS', meta={'current': j, 'total': 100, 'status': 'Read the CDG PRED data file.'});


    CDG_OMIM_KNOWN = pd.read_excel(home + "/Datasets/CDG_known.xlsx")
    j = 5 + (which)*90/length + 4*(90/length)/5 + 8*(90/length)/10
    self.update_state(state='PROGRESS', meta={'current': j, 'total': 100, 'status': 'Read the CDG KNOWN data file..'});


    print("Read first 4 CDG files")




    CDG_OMIM_KNOWN_Gene = CDG_OMIM_KNOWN['QUERY']
    CDG_HGMD_KNOWN_Gene = CDG_HGMD_KNOWN['gene']

    CDG_OMIM_PREDICTED_Gene_full = CDG_OMIM_PREDICTED['QUERY']
    CDG_OMIM_PREDICTED_Route_full = CDG_OMIM_PREDICTED['Route']


    CDG_OMIM_PREDICTED_Gene, CDG_OMIM_idx = np.unique(
        CDG_OMIM_PREDICTED_Gene_full, return_index=True)
    CDG_OMIM_PREDICTED_Route = CDG_OMIM_PREDICTED_Route_full[CDG_OMIM_idx]
    print("Read next 6 CDG files")


    CDG_HGMD_PREDICTED_Gene_full = CDG_HGMD_PREDICTED['Candidate gene']
    CDG_HGMD_PREDICTED_Route_full = CDG_HGMD_PREDICTED['Candidate-known route']
    CDG_HGMD_PREDICTED_Gene, CDG_HGMD_idx = np.unique(
        CDG_HGMD_PREDICTED_Gene_full, return_index=True)
    CDG_HGMD_PREDICTED_Route = CDG_HGMD_PREDICTED_Route_full[CDG_HGMD_idx]
    print("Read next 4 CDG files")


    CDG_HGMD_ROUTE_dict = dict(
        zip(CDG_HGMD_PREDICTED_Gene, CDG_HGMD_PREDICTED_Route))
    CDG_OMIM_ROUTE_dict = dict(
        zip(CDG_OMIM_PREDICTED_Gene, CDG_OMIM_PREDICTED_Route))
    print("Read next 2 CDG files")



    print("CDG Access")
    CDG_HGMD_KNOWN, CDG_OMIM_KNOWN, CDG_HGMD_ROUTE, CDG_OMIM_ROUTE = CDG_func(self, num_genes, CDG_HGMD_KNOWN_Gene, CDG_OMIM_KNOWN_Gene, CDG_HGMD_ROUTE_dict, CDG_OMIM_ROUTE_dict, gene, length, which)


    j = 5 + (which + 1)*90/length
    self.update_state(state='PROGRESS', meta={'current': j, 'total': 100, 'status': 'Completed CDG HGMD and OMIM Annotations.'});


    print("MSC")
    se = pd.Series(MSC_values)  # convert the list to a series
    # add the series as a column to the input file
    output_data['MSC'] = se.values
    print("pLI")
    se1 = pd.Series(pLI_matched)  # convert the list to a series
    # add the series as a column to the input file
    output_data['pLI'] = se1.values
    print("pRec")
    se2 = pd.Series(pRec_matched)  # convert the list to a series
    # add the series as a column to the input file
    output_data['pRec'] = se2.values
    print("pNull")
    se3 = pd.Series(pNull_matched)  # convert the list to a series
    # add the series as a column to the input file
    output_data['pNull'] = se3.values
    print("GDI")
    se4 = pd.Series(GDI_matched)  # convert the list to a series
    # add the series as a column to the input file
    output_data['GDI'] = se4.values
    print("GDI_Phred")
    se5 = pd.Series(GDI_Phred_matched)  # convert the list to a series
    # add the series as a column to the input file
    output_data['GDI_Phred'] = se5.values
    print("CDG 4 cols")
    se6 = pd.Series(CDG_HGMD_KNOWN)  # convert the list to a series
    # add the series as a column to the input file
    output_data['CDG_HGMD_PREDICTED'] = se6.values
    se7 = pd.Series(CDG_HGMD_ROUTE)  # convert the list to a series
    # add the series as a column to the input file
    output_data['CDG_HGMD_KNOWN'] = se7.values
    se8 = pd.Series(CDG_OMIM_KNOWN)  # convert the list to a series
    # add the series as a column to the input file
    output_data['CDG_OMIM_PREDICTED'] = se8.values
    se9 = pd.Series(CDG_OMIM_ROUTE)  # convert the list to a series
    # add the series as a column to the input file
    output_data['CDG_OMIM_KNOWN'] = se9.values



    try:
        output_data = output_data.drop(columns=['Unnamed: 0'], axis=1)
    except Exception as e:
        print(e)
    finally:
        return output_data

# Annotation. Actual Scripts for Processing.
@celery.task(bind=True)
def annotate_my_directory(self, home, mypath, filenames):
    print("CELERY TASK ANNOTATE CALLED :)) ")
    # print("## Celery Task WES_CLEANING called.")
    os.chdir(mypath)
    # Retrieve rough number of columns. This is a little repetitive since we
    # are going to read this dataframe again, but it is required to have an
    # accurate estimate of how long it'll take for our progressbar, and when
    # we should update the bar.
    if filenames[0].endswith('.csv'):
        t = pd.read_csv(filenames[0])
        t = t.reset_index(drop=True)

    elif filenames[0].endswith('xlsx'):
        t = pd.read_excel(filenames[0])
        t = t.reset_index(drop=True)

    # total: Number of iterations needed across all files.
    # i: our iterate.
    length = len(filenames)
    total = len(filenames) * len(t.columns)
    i = 0

    perc = 0
    # 1. Read files as dataframes.
    wANNOVAR_data_list = []
    for file in filenames:
        if file.endswith('.csv'):
            x = pd.read_csv(file)
            x = x.reset_index(drop=True)

        elif file.endswith('.xlsx'):
            x = pd.read_excel(file)
            x = x.reset_index(drop=True)

        wANNOVAR_data_list.append(x)

    perc = perc + 5

    print("About to update now. ")
    self.update_state(state='PROGRESS', meta={'current': perc, 'total': 100, 'status': 'Read all your files'})

    which = 0
    wANNOVAR_data_annotated_list = []
    for wANNOVAR_data in wANNOVAR_data_list:
        y = annotate(self, wANNOVAR_data, home, length, which)
        which = which + 1
        print("Completed annotation for FILE i")

        wANNOVAR_data_annotated_list.append(y)

    print("Finished annotating, now creating directory structure.")
    # Make a results directory
    if os.path.exists('res') == False:
        os.mkdir('res')

    k = 0
    for y in wANNOVAR_data_annotated_list:
        # Write the result dataframe into that directory
        y.to_csv('res/' + filenames[k].rsplit('.', 1)[0] + '_anno.csv', index=None)
        k = k + 1

    self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Completed Annotations.'});

    os.chdir(home)
    return {'current':100, 'total':100, 'status': 'Task Completed!', 'result': 100}


###############################################################################
@celery.task(bind=True)
def filter_my_directory(self, home, mypath, filenames, gdi, maf, mafCol):
    print("CELERY TASK FILTER CALLED :)) ")

    # print("## Celery Task WES_CLEANING called.")
    os.chdir(mypath)
    # Retrieve rough number of columns. This is a little repetitive since we
    # are going to read this dataframe again, but it is required to have an
    # accurate estimate of how long it'll take for our progressbar, and when
    # we should update the bar.
    if filenames[0].endswith('.csv'):
        t = pd.read_csv(filenames[0])
        t = t.reset_index(drop=True)

    elif filenames[0].endswith('xlsx'):
        t = pd.read_excel(filenames[0])
        t = t.reset_index(drop=True)

    # total: Number of iterations needed across all files.
    # i: our iterate.
    i = 0
    perc = 0

    # 1. Read files as dataframes.
    wANNOVAR_data_list = []
    for file in filenames:
        if file.endswith('.csv'):
            x = pd.read_csv(file)
            x = x.reset_index(drop=True)

        elif file.endswith('.xlsx'):
            x = pd.read_excel(file)
            x = x.reset_index(drop=True)

        wANNOVAR_data_list.append(x)

    perc = perc + 5
    self.update_state(state='PROGRESS', meta={'current': perc, 'total': 100, 'status': 'Read all your files'})

    which = 0
    wANNOVAR_data_filtered_list = []
    length = len(wANNOVAR_data_list)

    GDICutoff = gdi
    MAFCutoff = maf
    MAFColumn = mafCol

    for input_data in wANNOVAR_data_list:
        geneLevelFilteredData = pd.DataFrame(columns=input_data.columns)
        GDICutoff = 1000
        GDI = [0] * len(input_data[MAFColumn]);

        # if not GDICutoff:
        #     print("GDI was empty")
        #     # Has to be a large enough value, because this is an upper bound that shouldn't matter.
        #     # Since it's normalized, anything around 1000
        #     GDICutoff = 1000
        #     GDI = [0] * len(input_data[MAFColumn]);
        # else :
        #     GDI = [0] * len(input_data[MAFColumn]);
        #
        #     GDI = list(input_data['GDI_Phred'])

        MAF = list(input_data[MAFColumn])
        row_shape =input_data.shape[0]
        for j in range(row_shape):
            GDICondition = float(GDI[j]) < float(GDICutoff) or pd.isnull(GDI[j])
            MAFCondition = MAF[j] == '.' or float(
                MAF[j]) < float(MAFCutoff) or pd.isnull(MAF[j])
            #CompareCondition = (leftCompare == rightCompare) or np.isnan(leftValues[j]) or rightValues[j] == '.' or (float(leftValues[j]) < float(rightValues[j]))

            if GDICondition and MAFCondition:  # and CompareCondition:
                geneLevelFilteredData = geneLevelFilteredData.append(
                    input_data.iloc[j])

            self.update_state(state='PROGRESS', meta={'current': 5 + which*90/length + j*90/(length*row_shape), 'total': 100, 'status': 'Completed Filtering.'});

        self.update_state(state='PROGRESS', meta={'current': 5 + (which + 1)*90/length, 'total': 100, 'status': 'Completed Filtering.'});

        y = geneLevelFilteredData

        print("Completed filtering for FILE i")

        wANNOVAR_data_filtered_list.append(y)
        which = which + 1

    print("Finished filtering, now creating directory structure.")
    perc = 95
    self.update_state(state='PROGRESS', meta={'current': perc, 'total': 100, 'status': 'Read all your files'})

    # Make a results directory
    if os.path.exists('res') == False:
        os.mkdir('res')

    k = 0
    for y in wANNOVAR_data_filtered_list:
        # Write the result dataframe into that directory
        y.to_csv('res/' + filenames[k].rsplit('.', 1)[0] +
                 '_MAF' + MAFCutoff + '.csv', index=None)
        k = k + 1

    self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Completed Filtering.'});

    os.chdir(home)
    return {'current':100, 'total':100, 'status': 'Task Completed!', 'result': 100}

def genefilter(input_data, home, GDICutoff, MAFCutoff, MAFColumn):

    geneLevelFilteredData = pd.DataFrame(columns=input_data.columns)
    if not GDICutoff:
        print("GDI was empty")
        # Has to be a large enough value, because this is an upper bound that shouldn't matter.
        # Since it's normalized, anything around 1000
        GDICutoff = 1000
        GDI = [0] * len(input_data[MAFColumn]);
    else :
        GDI = list(input_data['GDI_Phred'])

    MAF = list(input_data[MAFColumn])

    for j in range(input_data.shape[0]):
        GDICondition = float(GDI[j]) < float(GDICutoff) or pd.isnull(GDI[j])
        MAFCondition = MAF[j] == '.' or float(
            MAF[j]) < float(MAFCutoff) or pd.isnull(MAF[j])
        #CompareCondition = (leftCompare == rightCompare) or np.isnan(leftValues[j]) or rightValues[j] == '.' or (float(leftValues[j]) < float(rightValues[j]))

        if GDICondition and MAFCondition:  # and CompareCondition:
            geneLevelFilteredData = geneLevelFilteredData.append(
                input_data.iloc[j])

    return geneLevelFilteredData

###########################################################
########## MODES OF INHERITANCE MASTER METHOD #############
###########################################################
# Examples of the format the input needs to be in

# inputFiles = ['../wannovar files family/BH7922_3_wANNOVAR_prefilter_anno_pred.csv', '../wannovar files family/BH7922_5_wANNOVAR_minimal_prefilter_anno_pred.csv']
# outputFiles = ['sampleoutput1.csv', 'sampleoutput2.csv']
# zygCheck = ['het',['het', 'abs']]
# extra = [False, False, True, 2] -- these represent x-linked and compound het states booleans, and the HGNC stuff, and the patient ix if comphet is true.

@celery.task(bind=True)
def modesOfInheritance(self, mypath, onlyfiles, zygCheck, extra):

    os.chdir(mypath)
    # Once the files are read, execute our python script/
    dfArray = []
    for file in onlyfiles:
        if file.endswith('.csv'):
            x = pd.read_csv(file)
            x = x.reset_index(drop=True)

        elif file.endswith('.xlsx'):
            x = pd.read_excel(file)
            x = x.reset_index(drop=True)

        dfArray.append(x);

    print("Length of stored files: ", len(dfArray))

    patient = dfArray[0];
    family = dfArray[1:];
    name = 0

    print(zygCheck)
    print(extra)
    #number_of_files = len(inputFiles)

    # compound heterozygous -- i'm assuming its a trio for now, i don't know how the bio of compund het would
    # work with bigger families
    if extra[1] == True:

        # Modify what's the patient and what's the family, since compHet was checked..
        patient = dfArray[extra[-1]]
        dfArray.pop(extra[-1])
        family = dfArray
        name = extra[-1]

        candidates1 = masterMethod(self, patient, family, ['het', ['het', 'absent']], (True, 0))
        candidates2 = masterMethod(self, patient, family, ['het', ['absent', 'het']], (True, 1))
        # this is just a domain trick.
        candidates1['owner'] = 1
        candidates2['owner'] = 2
        candidates1.index = range(0, len(candidates1))
        candidates2.index = range(0, len(candidates2))
        candidates = pd.concat([candidates1, candidates2], ignore_index=True)
        candidates = candidates.sort_values(['Gene.refGene'])
        candidates.index = range(0, len(candidates))
        genemapx = dict()
        genemapy = dict()

        for i in range(0, len(candidates)):
            # Hopefully, default value is 0.
            if candidates.loc[i, 'owner'] == 1:
                genemapx[candidates.loc[i, 'Gene.refGene']] = genemapx.get(
                    candidates.loc[i, 'Gene.refGene'], 0) + 1
            elif candidates.loc[i, 'owner'] == 2:
                genemapy[candidates.loc[i, 'Gene.refGene']] = genemapy.get(
                    candidates.loc[i, 'Gene.refGene'], 0) + 1

        can_genes = []
        print(genemapx)
        print(genemapy)
        for k in genemapx.keys() & genemapy.keys():
            can_genes.append(k)

        candidates = candidates[candidates['Gene.refGene'].isin(can_genes)]

        v = candidates['Gene.refGene'].value_counts()

    else:
        candidates = masterMethod(self, patient, family, zygCheck, (False, -1))

    candidates.index = range(0, len(candidates))
    #candidates = candidates.drop(['Unnamed: 0.1'], axis=1)
    list_of_x = ['X', 'chrX']

    # This is the statement required to deal with X-linked mutations, just filters out the X
    if extra[0] == True:
        candidates = candidates[candidates['Chr'].isin(list_of_x)]

    # Compound heterozygous, same gene variants condition
    if extra[1] == True:
        candidates = candidates.groupby('Gene.refGene').filter(lambda y: len(y) > 1)

    candidates.index = range(0, len(candidates))

    # The user wants the gene name as well.
    if extra[2] == True:
        ### Add gene name annotations here....
        genes = pd.read_csv("../data/geneinfo.txt", sep='\t')
        genedict = {}
        for i in range(0, genes.shape[0]):
            genedict[genes.loc[i, 'Approved symbol']] = genes.loc[i, 'Approved name']

        ix_gene = list(candidates.columns).index('Gene.refGene')
        candidates.insert(ix_gene + 2,'HGNC Gene Name',0 )

        for i in range(0, candidates.shape[0]):
                candidates.loc[i, 'HGNC Gene Name'] = annotate_gene(genedict, genes, candidates.loc[i, 'Gene.refGene'])
                print(candidates.loc[i, 'HGNC Gene Name'])

        j = 95
        self.update_state(state='PROGRESS', meta={'current': j, 'total': 100, 'status': 'Completed HGNC Gene Name Annotations.'});

    ###################
    ###################


    print("Finished modes of Inheritance analysis, now creating directory structure.")
    # Make a results directory
    if os.path.exists('res') == False:
        os.mkdir('res')

    # wANNOVAR cleaned list contains clean dataframes. So we're going to prefilter them as well
    # in this step. And, then output everything in one go.

    candidates.to_csv('res/' + onlyfiles[name].rsplit('.', 1)[0] + '_modes.csv',index=None )
    self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Completed HGNC Gene Name Annotations.'});

    return {'current':100, 'total':100, 'status': 'Task Completed!', 'result': 100}

def zygFilter(self, patient, refZyg):
    print("zygfilter")
    candidates = pd.DataFrame(columns=patient.columns)

    # Added this on March 1. Any filtering was not happening before.
    if refZyg == 'any':
        candidates = patient;
        candidates.index = range(0, len(candidates))
        return candidates;

    # Het or Abs filtering will happen like het.
    if refZyg == 'hetabs':
        for i in range(0, len(patient)):
            zyg = patient['zygosity'][i]
            if zyg == 'het':
                variant = patient.iloc[i]
                candidates = candidates.append(variant)
        candidates.index = range(0, len(candidates))
        print("returning ")
        print(candidates['zygosity'])
        return candidates

    # Otherwise.

    for i in range(0, len(patient)):
        zyg = patient['zygosity'][i]
        if zyg == refZyg:
            variant = patient.iloc[i]
            candidates = candidates.append(variant)

    candidates.index = range(0, len(candidates))

    print("returning ")
    print(candidates['zygosity'])
    return candidates

def masterMethod(self, patient, family, zygCheck, compHet):
    print ("master method")
    outputPatient = pd.DataFrame(columns=patient.columns)

    # It doesn't matter what the hypothesis is, you only need zygosities
    refZyg = zygCheck[0]
    otherZygs = zygCheck[1]
    print ("x")
    print(refZyg)
    print(otherZygs)

    candidates = zygFilter(self, patient, refZyg)

    perc = 5
    self.update_state(state='PROGRESS', meta={'current': perc, 'total': 100, 'status': 'Read all your files'})

    len_candidates = len(candidates)
    big_iter = 90/len_candidates
    which_parent = 0

    if compHet[0] == True:
        big_iter = 45/len_candidates
        which_parent = compHet[1]

    # do stuff with candidates
    for i in range(0, len_candidates):
        chrom = candidates['Chr'][i]
        start = candidates['Start'][i]
        end = candidates['End'][i]
        zyg = candidates['zygosity'][i]
        alt = candidates['Alt'][i]

        if candidateCheck(self, family, chrom, start, end, alt, otherZygs, i, big_iter, which_parent*45 ) == True:
            variant = candidates.iloc[i]
            outputPatient = outputPatient.append(variant)
            # keep this variant in patient file

        self.update_state(state='PROGRESS', meta={'current': 5 +  which_parent*45  + (i + 1)*big_iter, 'total': 100, 'status': 'Read another candidate.'})

    return outputPatient

def checkThisPerson(self, person, chrom, start, end, alt, zygShould, summand, med_iter, compHet):
    sm_iter = med_iter/len(person)

    # I don't want to find this variant in this person
    if zygShould == 'absent':
        print ("Absent Check")
        for y in range(0, len(person)):
            chrom2 = person['Chr'][y]
            start2 = person['Start'][y]
            end2 = person['End'][y]
            alt2 = person['Alt'][y]

            # This variant was found, return false immediately (because it is not absent)
            if chrom2 == chrom and start2 == start and end2 == end and alt2 == alt:
                print ("Variant present in family member")
                return False

            # self.update_state(state='PROGRESS', meta={'current': summand + compHet + y*sm_iter, 'total': 100, 'status': 'Read another variant'})

        # If this variant wasn't found in this person
        print ("Variant absent in this family member")
        return True

    # Variant can be present or not
    elif zygShould == 'any':
        print ("Skipping family member because variant can be present or absent according to user")
        return True

    elif zygShould == 'hom':
        for y in range(0, len(person)):
            chrom2 = person['Chr'][y]
            start2 = person['Start'][y]
            end2 = person['End'][y]
            alt2 = person['Alt'][y]
            zyg2 = person['zygosity'][y]

            # This variant was found, return false immediately (because it is not absent)
            if chrom2 == chrom and start2 == start and end2 == end and alt2 == alt and zyg2 == zygShould:
                print ("Homozygous variant found in family member")
                return True

            # self.update_state(state='PROGRESS', meta={'current': summand + y*sm_iter, 'total': 100, 'status': 'Read another variant'})


        # If a h0o variant wasn't found in this person
        print ("Homozygous variant absent in this family member")
        return False

    elif zygShould == 'het':
        for y in range(0, len(person)):
            chrom2 = person['Chr'][y]
            start2 = person['Start'][y]
            end2 = person['End'][y]
            alt2 = person['Alt'][y]
            zyg2 = person['zygosity'][y]

            # This variant was found, return false immediately (because it is not absent)
            if chrom2 == chrom and start2 == start and end2 == end and alt2 == alt and zyg2 == zygShould:
                print( "Heterozygous variant found in family member")
                return True


            # self.update_state(state='PROGRESS', meta={'current': summand + y*sm_iter, 'total': 100, 'status': 'Read another variant'})


        # If a het variant wasn't found in this person
        print ("Heterozygous variant absent in this family member")
        return False

    elif zygShould == 'hetabs':
        for y in range(0, len(person)):
            chrom2 = person['Chr'][y]
            start2 = person['Start'][y]
            end2 = person['End'][y]
            alt2 = person['Alt'][y]
            zyg2 = person['zygosity'][y]

            # This variant was found, return false immediately (because it is not absent)
            if chrom2 == chrom and start2 == start and end2 == end and alt2 == alt:
                if zyg2 == 'het':
                    print( "Heterozygous variant found in family member")
                    return True
                elif zyg2 == 'hom':
                    print( "Homozygous variant found in family member. Not what we want.")
                    return False

            # self.update_state(state='PROGRESS', meta={'current': summand + y*sm_iter, 'total': 100, 'status': 'Read another variant'})

        print ("Variant absent in this family member")
        return True;

        # If a het variant wasn't found in this person

    else:
        print ("Zygosity not valid. Run again with hom, het, absent, any")

def candidateCheck(self, family, chrom, start, end, alt, otherZygs, which, big_iter, compHet):
    person_num = 0

    med_iter = big_iter
    if (len(family) != 0):
        med_iter /= len(family)

    if len(family) != len(otherZygs):
        print("Not enough info provided")
        return False
    else:
        for x in range(0, len(family)):
            # for an individual of family, check that variant has appropriate zyg
            if checkThisPerson(self, family[x], chrom, start, end, alt, otherZygs[x], 5 + which*big_iter + x* med_iter, med_iter , compHet) == False:
                return False

        return True





##########################
# UNBIASED COHORT ANALYSIS
##########################
@celery.task(bind=True)
def readcohortfiles(self, mypath, filenames, COLNAME, CUTOFF):

    os.chdir(mypath)

    print("In the cohort function,.")
    print(filenames)
    #STEP 1: MAKE ARRAY OF DATAFRAMES.
    data = []
    num_files = len(filenames)

    file_counter = 0
    print("PREPROCESSING: Reading all the files. ")
    for filex in filenames:
        if filex.endswith('.csv'):
            # temp = dd.read_csv(filex,dtype={'Chr': 'object'})
            temp = dd.read_csv(filex,dtype='str')
            temp = temp.reset_index(drop=True)

        elif filex.endswith('xlsx'):
            temp = pd.read_excel(filex, dtype ='str')
            temp = temp.reset_index(drop=True)
            temp = dd.from_pandas(temp, npartitions = 2)

        #STEP 2: Append filenames to each dataframe
        indices = [i for i, a in enumerate(filex) if a == '/']
        #start = indices[-1] + 1
        #end = start + 10
        c = '.'
        x = [pos for pos, char in enumerate(filex) if char == c][-1]
        x = x + 1
        temp['identifier'] = filex[0:(x - 1)] #all characters
        data.append(temp)

        self.update_state(state='PROGRESS', meta={'current': file_counter*5/num_files, 'total': 100, 'status': 'Reading all your files'})
        file_counter = file_counter + 1

    self.update_state(state='PROGRESS', meta={'current': 5, 'total': 100, 'status': 'Read all your files'})

    cols = data[0].columns
    combined = data[0]
    print("PREPROCESSING: Merging all the files into one HUGE database.")
    which_member = len(data) - 1
    member_counter = 0
    for member in data[1:len(data)]:
        combined = combined.append(member)

        self.update_state(state='PROGRESS', meta={'current': 5 + member_counter*5/which_member, 'total': 100, 'status': 'Read all your files'})

    combined = combined.reset_index()
    combined = combined.drop('index', axis = 1)
    # combined = combined.reindex(columns= cols)
    self.update_state(state='PROGRESS', meta={'current': 10, 'total': 100, 'status': 'Read all your files'})

    print("METHOD CALL: Calling unbiased cohort analysis method now.")
    print("SHAPEEEE" )
    print(combined.shape)
    output = unbiasedCohortEstimator(self, combined)
    cohortFilteredData = pd.DataFrame(columns=output.columns)

    MAF = list(output[COLNAME])
    print("HERE's the MAF " + str(MAF))
    num_rows_out = output.shape[0]
    for j in range(num_rows_out):

        MAFCondition = MAF[j] == '.' or float(
            MAF[j]) < float(CUTOFF) or pd.isnull(MAF[j])
        if MAFCondition:  # and CompareCondition:
            cohortFilteredData = cohortFilteredData.append(
                output.iloc[j])

        self.update_state(state='PROGRESS', meta={'current': 65 + j* 35/num_rows_out, 'total': 100, 'status': 'Filtering by MAF'})

    output = cohortFilteredData;


    self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Filtering by MAF'})


    print("CALL RETURNED: Finished analysis, now creating directory structure.")
    # Make a results directory
    if os.path.exists('res') == False:
        os.mkdir('res')

    output.to_csv('res/unbiasedCohortResults' + '_MAF' + CUTOFF   + '.csv', columns= cols, index=None )
    return {'current':100, 'total':100, 'status': 'Task Completed!', 'result': 100}

# INPUT PARAMS
#   data: array of dataframes, with identifiers appended already.
def unbiasedCohortEstimator(self, combined):
    #4. Rank genes by most frequent to least frequent by GENE
    #Exclude genes that occur only once (by default, they are occuring only in one patient)

    print("CORE: Parallelizing threads for faster processing.")
    counts = combined.groupby('Gene.refGene')['identifier'].apply(lambda x: x.value_counts()).compute()

    vals = list(counts.keys())
    genes_full_count = [i[0] for i in vals]
    genes = Counter(genes_full_count)
    gene_counts = genes.values()
    mask = map(lambda x: x>1,gene_counts )

    genes_to_include = list(compress(Counter(genes_full_count).keys(), mask))
    combined = combined[combined['Gene.refGene'].isin(genes_to_include)]

    print("CORE: Converting parallel threads into pandas dataframe.")
    combined_pandas = combined.compute()
    group2 = combined_pandas.groupby('Gene.refGene')
    df1 = group2.size().sort_values(ascending=False).reset_index(name='count')
    genestosort = df1['Gene.refGene']
    output = pd.DataFrame(columns=combined_pandas.columns)

    print("CORE: Sorting and pretty formatting your output. This steps takes the longest.")
    i = 0
    how_many_genes = len(genestosort)
    for rankgene in genestosort:
        print(str(round(i*100/len(genestosort),3)) + " %",end="\r")
        i = i + 1
        output = output.append(combined_pandas.loc[combined_pandas['Gene.refGene'] == rankgene])
        self.update_state(state='PROGRESS', meta={'current': 10 + i*55/how_many_genes, 'total': 100, 'status': 'Sorting genes.. '})

    return output



##########################
# BIASED COHORT ANALYSIS
##########################

def readCohortFiles(self, filenames):
    #STEP 1: MAKE ARRAY OF DATAFRAMES.
    data = []

    for filex in filenames:
        if filex.endswith('.csv'):
            temp = pd.read_csv(filex)
            temp = temp.reset_index(drop=True)
        elif filex.endswith('xlsx'):
            temp = pd.read_excel(filex)
            temp = temp.reset_index(drop=True)

        #STEP 2: Append filenames to each dataframe
        indices = [i for i, a in enumerate(filex) if a == '/']
        #start = indices[-1] + 1
        #end = start + 10
        c = '.'
        x = [pos for pos, char in enumerate(filex) if char == c][-1]
        x = x + 1
        temp['identifier'] = filex[0:(x - 1)] #all characters
        data.append(temp)

    cols = data[0].columns
    print(cols)
    # Combine all dataframes
    combined = data[0]
    for member in data[1:len(data)]:
        combined = combined.append(member)

    combined = combined.reset_index()
    combined = combined.drop(columns=['index'])

    combined = combined.reindex(columns= cols)
    print("Done reading")
    return combined


@celery.task(bind=True)
def biased_cohort_analysis(self, mypath, onlyfiles, GENE, COLNAME, CUTOFF):

    os.chdir(mypath)
    self.update_state(state='PROGRESS', meta={'current': 5, 'total': 100, 'status': 'Starting to read the files.. '})
    data = readCohortFiles(self, onlyfiles)

    self.update_state(state='PROGRESS', meta={'current': 10, 'total': 100, 'status': 'Done reading '})

    check1 = data['Gene.refGene'] == GENE;
    #check2 = data['Gene.refGene'].isnull();
    check2 = False;

    output = pd.DataFrame(columns=data.columns)

    length_data = len(data)
    for i in range(0, length_data):
        if check1[i]== True: #or check2[i]== True:
            output = output.append(data.iloc[i,:])

        self.update_state(state='PROGRESS', meta={'current': 10 + i*55/length_data, 'total': 100, 'status': 'Next row'})

    output_copy = output;
    cohortFilteredData = pd.DataFrame(columns=output.columns)
    print("Here")

    self.update_state(state='PROGRESS', meta={'current': 65, 'total': 100, 'status': 'Done extracting gene from cohort.  '})

    MAF = list(output[COLNAME])
    print(MAF)
    num_rows_out = output.shape[0]
    for j in range(num_rows_out):

        MAFCondition = MAF[j] == '.' or float(MAF[j]) < float(CUTOFF) or pd.isnull(MAF[j])
        print("CUTOFFFFFFF "  +CUTOFF)

        if MAFCondition:  # and CompareCondition:
            cohortFilteredData = cohortFilteredData.append(output.iloc[j])

        self.update_state(state='PROGRESS', meta={'current': 65 + j* 35/num_rows_out, 'total': 100, 'status': 'Filtering by MAF'})

    output_copy = cohortFilteredData;

    self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Filtering by MAF'})

    print("Finished biased cohort analysis, now creating directory structure.")
        # Make a results directory
    if os.path.exists('res') == False:
        os.mkdir('res')

    output_copy.to_csv('res/'+GENE+'.csv', index=None)
    return {'current':100, 'total':100, 'status': 'Task Completed!', 'result': 100}

##########################
# KINSHIP AND SEX INFERENCE
##########################
def kin_sex_script(home, mypath, filenames, bools, format):

    finpath = mypath + 'res/' + filenames[0].rsplit('.', 1)[0]
    arg = mypath + filenames[0].rsplit('.', 1)[0]
    if format == 'BED, BIM, FAM':
        pass_arg = ['./convert.sh', arg]
        subprocess.check_call(pass_arg)

    ## Check for the boolean of X and Y chromosome here. if if
    # If X chromosome:
    cwd = os.getcwd()
    if bools[0] == 'true':
            print("inside")
            pass_arg = ['./kin_sex_X.sh', arg]
            subprocess.check_call(pass_arg)
            os.chdir(mypath)
            try:
                os.mkdir('res')
                os.rename(arg + '_SEXCHECK.csv', finpath +'_SEXCHECK_X.csv')
            except FileExistsError:
                pass

    # If Y chromosome
    os.chdir(cwd)
    if bools[1] == 'true':
            print("inside")
            pass_arg = ['./kin_sex.sh', arg]
            subprocess.check_call(pass_arg)
            os.chdir(mypath)
            if os.path.exists('./res'):
                os.rename(arg + '_SEXCHECK.csv', finpath +'_SEXCHECK_Y.csv')

            try:
                os.mkdir('res')
                print("Renaming now. ")
                os.rename(arg + '_SEXCHECK.csv', finpath +'_SEXCHECK_Y.csv')
            except FileExistsError:
                pass


    os.chdir(cwd)
    if bools[0] == 'false' and bools[1] == 'false':
        pass_arg = ['./kin.sh', arg]
        subprocess.check_call(pass_arg)
        os.chdir(mypath)
        try:
            os.mkdir('res')
            os.rename(arg + '_kinshipScores.csv', finpath + '_kinshipScores.csv')
        except FileExistsError:
            pass
    else:
        os.chdir(mypath)
        os.rename(arg + '_kinshipScores.csv', finpath + '_kinshipScores.csv')

    os.chdir(home)
    return jsonify()


##########################
# ANCESTRY INFERENCE HELPERS
##########################
def whatMarkersBIM(f):
    markers =[]
    i = 0
    for line in f:
        try:
            x = f.readline().strip().split('\t')
            markers.append(x[1])
        except IndexError:
            print('ISSUE' + str(i))
            pass
        i = i + 1
        if (i %100000 == 0):
        #print(i)
            pass
    return markers

@celery.task(bind=True)
def ancestry_script(self, home, mypath, filenames, format):
    self.update_state(state='PROGRESS', meta={'current': 1, 'total': 100, 'status': 'Started ancestry script'})

    print("Home: ", home)
    print("mypath: ", mypath)
    print("filenames: ", filenames)
    print("Format: ", format)

    arg = mypath + filenames[0].rsplit('.', 1)[0]
    print("ARGGGG : ", arg)

    finpath = mypath + 'ancestry_buffer/'


    print("Arg: ", arg)
    print("finpath: ", finpath)


    #### 1...  We want to convert the PED/MAP files to BED,BIM,FAM. Becuase we're merging binaries.
    if format == 'PED, MAP':
        print("We want to convert the PED/MAP files to BED,BIM,FAM. Becuase we're merging binaries")
        pass_arg = ['./convert2ped.sh', arg]
        subprocess.check_call(pass_arg)
        print("Done.")

    if format == 'BED, BIM, FAM':
        pass_arg = ['./convert.sh', arg]
        subprocess.check_call(pass_arg)

    self.update_state(state='PROGRESS', meta={'current': 5, 'total': 100, 'status': 'Started ancestry script'})

    cwd = os.getcwd()
    print("CWD: ", cwd)

    #### 2... Next, we will try to run python code to get common markers, before we start the extraction process.
    print(" Next, we will try to run python code to get common markers, before we start the extraction process.")
    data = []
    # This won't work if you started with 'BED, BIM FAM.. so also recodee... '
    f = open(arg + '.ped')
    i = 0
    for line in f:
        piece = line.strip().split(' ')
        data.append(piece)

    cwd = os.getcwd()

    os.chdir(mypath)
    if os.path.exists('ancestry_buffer') == False:
        os.mkdir('ancestry_buffer')

    os.chdir(cwd)
    sandbox_path = '../../../webseq_sandbox/'
    sample_markers = list(pd.read_csv(arg + '.map', sep = '\t', header = -1)[1].values)
    print("Reading all markers through chromosmes 1-4")
    # f = open('./Datasets/ancestry_data/chr1-4.bim')
    f = open(sandbox_path + "SNP_Analysis_Reference_Data/ancestry_data/chr1-4.bim")
    master_markers = whatMarkersBIM(f)

    self.update_state(state='PROGRESS', meta={'current': 5 + 65/3, 'total': 100, 'status': 'Started ancestry script'})

    print("Reading all markers through chromosmes 5-8")
    # f = open('./Datasets/ancestry_data/chr5-8.bim')
    f = open(sandbox_path + "SNP_Analysis_Reference_Data/ancestry_data/chr5-8.bim")
    master_markers += whatMarkersBIM(f)

    self.update_state(state='PROGRESS', meta={'current': 5 + 2*65/3, 'total': 100, 'status': 'Started ancestry script'})


    print("Reading all markers through chromosmes 9-X")
    # f = open('./Datasets/ancestry_data/chr9-X.bim')
    f = open(sandbox_path + "SNP_Analysis_Reference_Data/ancestry_data/chr9-X.bim")
    master_markers += whatMarkersBIM(f)

    self.update_state(state='PROGRESS', meta={'current': 70, 'total': 100, 'status': 'Started ancestry script'})

    common_markers = list(set(sample_markers).intersection(master_markers))

    print(len(common_markers) , ' common markers')

    if len(common_markers) == 0:
        # Basically, don't do anything else.
        print("No markersss, don't continue with analysis. ")
        self.update_state(state='ERROR', meta={'current': 70, 'total': 100, 'status': 'No common markers found.', 'err': -1})
        raise Ignore()
        return {'state': 'ERROR', 'current':70, 'total':100, 'status': 'Task not completed!', 'err': -1}

    np.savetxt('./data/common_markers.txt', common_markers, fmt='%s')
    print("Go check if the file was saved properly in the data folder.")

    #### 3... Next step is to attempt to merge the two datasets, and save intermediate files (chr1-X, and merge3) in the data folder.
    #3 cd into CWD
    print('.')
    print('.')
    print('.')
    print("Next step is to attempt to merge the two datasets, and save intermediate files (chr1-X, and merge3) in the data folder.")
    print('.')
    print('.')
    print('.')
    pass_arg = ['./merge.sh', arg]
    try:
        subprocess.check_call(pass_arg)
    except CalledProcessError:
        self.update_state(state='ERROR', meta={'current': 70, 'total': 100, 'status': 'Duplicate id or merge issue.', 'err': -2})
        raise Ignore()
        return {'state': 'ERROR', 'current':70, 'total':100, 'status': 'Task not completed!', 'err': -1}

    print("Done.")

    ### DONE THEN... RETURN JSONIFY, AND MAKE THE PANEL AVAILABLE...
    self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Started ancestry script'})

    os.chdir(home)
    return {'current':100, 'total':100, 'status': 'Task Completed!', 'result': 100}

def gen_pcs(PC1, PC2):
    df = pd.read_excel('./Datasets/20130606_sample_info.xlsx')

    q = df['Sample']
    r = df['Population']
    df = pd.concat([q,r], axis=1)

    pops = list(df['Population'].values)

    ######
    # NEED TO EXECUTE THE PCA GENERATION CODE HERE... THIS IS WHY WE WEREN'T ABLE TO GET GOOD RESOLUTION..
    # WE WILL NOWW HOPEFULLYY. SAMPLES + PATIENT + FEW MORE:)))
    # pass_arg = ['./gen_pcs.sh', arg]
    try:
        eigenvecs = pd.read_csv('./temp/ancestry_buffer/merge3_pca.eigenvec', sep = ' ', header = -1)
    except:
        return -3

    # 'HG00096' is the first sample in 1000G.. That's how many samples the researcher uploaded.
    # num_samples = list(eigenvecs[0]).index('HG00096')
    num_samples = 0
    for i in range(0, len(eigenvecs[0])):
        try:
            ix = list(df['Sample']).index(eigenvecs[0][i])
            num_samples = i
            break;
        except ValueError:
            pass;



    #and key dictionaries for 1000G Ancestry Plots.
    with open('./defaults.json') as json_file:
        default = json.load(json_file)
        cdict = default["cdict"]
        key_dict = default["key_dict"]
    # cdict = {
    # 'GBR':'#1eedd4', # GBR	British in England and Scotland
    # 'TSI':'#185b7a', # TSI	Toscani in Italia
    # 'FIN':'#4414db', # FIN	Finnish in Finland
    # 'CEU':'#91dfb7', # CEU	Utah Residents (CEPH) with Northern and Western European Ancestry
    #
    # 'IBS':'#9b224a', # IBS	Iberian Population in Spain
    # 'MXL':'#610625', # MXL	Mexican Ancestry from Los Angeles USA
    # 'PUR':'#991404', # PUR	Puerto Ricans from Puerto Rico
    # 'CLM':'#dc4e54', # CLM	Colombians from Medellin, Colombia
    # 'PEL':'#cc6fca', # PEL	Peruvians from Lima, Peru
    #
    # 'GIH':'#196b04', # GIH	Gujarati Indian from Houston, Texas
    # 'BEB':'#414127', # BEB	Bengali from Bangladesh
    # 'ITU':'#60db82', # ITU	Indian Telugu from the UK
    # 'PJL':'#8ccd0c', # PJL	Punjabi from Lahore, Pakistan
    # 'STU':'#068b81', # STU	Sri Lankan Tamil from the UK
    #
    # 'CDX':'#d6b3da', # CDX	Chinese Dai in Xishuangbanna, China
    # 'CHB':'#c59b88', # CHB	Han Chinese in Beijing, China
    # 'CHS':'#c29d44', # CHS	Southern Han Chinese
    # 'KHV':'#4a2014', # KHV	Kinh in Ho Chi Minh City, Vietnam
    # 'JPT':'#44886e', # JPT	Japanese in Tokyo, Japan
    #
    #
    # 'LWK':'#40E0D0', # LWK	Luhya in Webuye, Kenya
    # 'MSL':'#F08080', # MSL	Mende in Sierra Leone
    # 'YRI':'#4d575f', # YRI	Yoruba in Ibadan, Nigeria
    # 'GWD':'#543252', # GWD	Gambian in Western Divisions in the Gambia
    # 'ESN':'#4a5650', # ESN	Esan in Nigeria
    # 'ASW':'#ef831e', # ASW	Americans of African Ancestry in SW
    # 'ACB':'#4fd988'  # ACB	African Caribbeans in Barbados
    # }
    # key_dict = {
    # 'GBR':'British in England and Scotland',
    # 'TSI':'Toscani in Italia',
    # 'FIN':'Finnish in Finland',
    # 'CEU':'Utah Residents (CEPH) with Northern and Western European Ancestry',
    #
    # 'IBS':'Iberian Population in Spain',
    # 'MXL':'Mexican Ancestry from Los Angeles USA',
    # 'PUR':'Puerto Ricans from Puerto Rico',
    # 'CLM':'Colombians from Medellin, Colombia',
    # 'PEL':'Peruvians from Lima, Peru',
    #
    # 'GIH':'Gujarati Indian from Houston, Texas',
    # 'BEB':'Bengali from Bangladesh',
    # 'ITU':'Indian Telugu from the UK',
    # 'PJL':'Punjabi from Lahore, Pakistan',
    # 'STU':'Sri Lankan Tamil from the UK',
    #
    # 'CDX':'Chinese Dai in Xishuangbanna, China',
    # 'CHB':'Han Chinese in Beijing, China',
    # 'CHS':'Southern Han Chinese',
    # 'KHV':'Kinh in Ho Chi Minh City, Vietnam',
    # 'JPT':'Japanese in Tokyo, Japan',
    #
    #
    # 'LWK':'Luhya in Webuye, Kenya',
    # 'MSL':'Mende in Sierra Leone',
    # 'YRI':'Yoruba in Ibadan, Nigeria',
    # 'GWD':'Gambian in Western Divisions in the Gambia',
    # 'ESN':'Esan in Nigeria',
    # 'ASW':'Americans of African Ancestry in SW',
    # 'ACB':'African Caribbeans in Barbados'
    # }


    sample = eigenvecs.iloc[:num_samples,:].iloc[:,1:]
    ref = pd.concat([eigenvecs.iloc[num_samples:,:][0], eigenvecs.iloc[num_samples:,:].iloc[:,2:]], axis= 1)
    ref.columns = list(range(0,ref.shape[1]))
    sample.columns = list(range(0, sample.shape[1]))

    mask = []
    for i in range(0,df.shape[0]):
        mask.append(df['Sample'][i] in list(eigenvecs[0].values))

    df = df.loc[mask, :]
    df = df.reset_index(drop=True)


    data = []
    for g in np.unique(df['Population']):
        ix = np.where(df['Population'] == g)
        trace = go.Scatter(x=ref.iloc[ix[0],PC1], y=ref.iloc[ix[0],PC2],mode = 'markers', marker=dict(color = cdict[g]),name=g, text=key_dict[g])
        data.append(trace)

    for j in range(0, sample.shape[0]):
        sample_trace = go.Scatter(x = np.array(sample[PC1][j]), y = np.array(sample[PC2][j]), mode='markers',marker=dict(color = 'yellow', size = 7,line = dict(
                width = 2,
            )), name= sample[0][j], text=sample[0][j])
        data.append(sample_trace)

    layout= go.Layout(
        title= 'Population Inference: Reference + Study Samples',
        hovermode= 'closest',
        xaxis= dict(
            title= 'PC ' + str(PC1),
            ticklen= 5,
            zeroline= False,
            gridwidth= 2,
        ),
        yaxis=dict(
            title= 'PC ' + str(PC2),
            ticklen= 5,
            gridwidth= 2,
        ),
    )

    fig= go.Figure(data=data, layout=layout)


    plot_div = plot(fig, auto_open=False, filename="./static/temp-plot.html")
    plio.to_html(fig)

    return 0


##########################
# BLACKLIST GENERATION
##########################

@celery.task(bind=True)
def blacklist_generation(self, mypath, onlyfiles, CUTOFF):

    num_patients = len(onlyfiles)

    vardict = {}
    for num in range(0, num_patients):

        print("Exome " + str(num) + " out of " + str(num_patients),end='\r')
        if onlyfiles[num].endswith('.csv'):
            patient = pd.read_csv(mypath+ onlyfiles[num])
            patient = patient.reset_index(drop=True)
        elif onlyfiles[num].endswith('.xlsx'):
            patient = pd.read_excel(mypath + onlyfiles[num])
            patient = patient.reset_index(drop=True)

        # To check if a variant has been seen already in this very patient.
        seen = set()

        cols = list(patient.columns)
        chr_ix = cols.index('Chr')

        start_ix = cols.index('Start')
        end_ix = cols.index('End')
        ref_ix = cols.index('Ref')
        alt_ix = cols.index('Alt')

        # Check if variant is in the seen SET or not.
        # If YES: SKIP
        # If NO: add it to the set

        # Add variant to a VARDICT
        num_rows_in_patient = patient.shape[0]
        for row in range(0,num_rows_in_patient ):
            var = list(patient.iloc[row,[chr_ix, start_ix, end_ix, ref_ix, alt_ix]].values)
            var = [str(i) for i in var]
            var = ','.join(var)

            if var in seen:
    #             print("REPEAT")
                # Need to skip this iteration.
                continue;
            else:
    #             print("NEW")
                seen.add(var)

            if var not in vardict:
    #             print("ADDED")
                vardict[var] = 1
            else:
    #             print("FOUND")
                vardict[var] += 1

            self.update_state(state='PROGRESS', meta={'current': num*90/num_patients + row*90/(num_patients*num_rows_in_patient), 'total': 100, 'status': 'Next variant in patient '})

        self.update_state(state='PROGRESS', meta={'current': (num + 1)*90/num_patients, 'total': 100, 'status': 'Next File..  '})

    # Deletes the seen variable.
    del seen




    condensed_dict = {}

    for var in vardict:
        key = ','.join(var.split(',')[:3])

        if key not in condensed_dict:
            condensed_dict[key] = [vardict[var], [var]]
        else:
            condensed_dict[key][0] += int(vardict[var])
            condensed_dict[key][1].append(var)

    blacklist = []
    for chr_pos in condensed_dict:
        var_pts = condensed_dict[chr_pos][0]

        if var_pts/num_patients > CUTOFF :
            if var_pts > num_patients:
                shared_pt_num = num_patients
            else:
                shared_pt_num = var_pts
            length = len(condensed_dict[chr_pos][1])
            for var in condensed_dict[chr_pos][1]:
                split = var.split(',')
                towrite = '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\n'.format(split[0], split[1], split[2], split[3], split[4], shared_pt_num, vardict[var], length, num_patients )
                blacklist.append(towrite)

    self.update_state(state='PROGRESS', meta={'current': 98, 'total': 100, 'status': 'Next File..  '})


    blacklist = pd.DataFrame([sub.strip().split("\t") for sub in blacklist ], columns=['Chr', 'Start', 'End', 'Ref', 'Alt', 'Shared', 'Num Patients', 'Len', 'Total'])

    dt = datetime.datetime.now()
    # str.format
    date = '{:%d%B%Y}'.format(dt)

    os.chdir(mypath)
    if os.path.exists('res') == False:
        os.mkdir('res')

    blacklist.to_csv('res/blacklist' + str(CUTOFF) + '_' + date + '.csv', index=None)

    self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Done'})

    return {'current':100, 'total':100, 'status': 'Task Completed!', 'result': 100}

##########################
# BLACKLIST APPLY
##########################

@celery.task(bind=True)
def apply_blacklist(self, mypath, onlyfiles, blacklist_file_name, checksort):


    if blacklist_file_name.endswith('.csv'):
        blacklist = pd.read_csv(mypath + blacklist_file_name)
        blacklist = blacklist.reset_index(drop=True)
        print(blacklist.columns)

    elif blacklist_file_name.endswith('.xlsx'):
        blacklist = pd.read_csv(mypath + blacklist_file_name)
        blacklist = blacklist.reset_index(drop=True)

    filter_info = blacklist.iloc[:,:5]
    chr_values = list((filter_info['Chr']).values)
    start_values = list((filter_info['Start']).values)
    end_values = list((filter_info['End']).values)
    ref_values = list((filter_info['Ref']).values)
    alt_values = list((filter_info['Alt']).values)

    self.update_state(state='PROGRESS', meta={'current': 5, 'total': 100, 'status': 'Read your blacklist'})

    os.chdir(mypath)
    if os.path.exists('res') == False:
        os.mkdir('res')

    blacklisted_result_files = []

    num_files = len(onlyfiles)
    which_file = 0

    for file in onlyfiles:
        if file.endswith('.csv'):
            ranks = pd.read_csv(file)
            ranks = ranks.reset_index(drop=True)
        elif file.endswith('.xlsx'):
            ranks = pd.read_excel(file)
            ranks = ranks.reset_index(drop=True)

        final = pd.DataFrame()
        delete = 0
        ranks_shape = ranks.shape[0]
        for i in range(0, ranks_shape):
            bool1 = ranks.loc[i,'Chr'] in list((filter_info['Chr']).values)
            bool2 = ranks.loc[i,'Start'] in list((filter_info['Start']).values)
            bool3 = ranks.loc[i,'End'] in list((filter_info['End']).values)
            bool4 = ranks.loc[i,'Ref'] in list((filter_info['Ref']).values)
            bool5 = ranks.loc[i,'Alt'] in list((filter_info['Alt']).values)

            if bool1 and bool2 and bool3 and bool4 and bool5:
                delete = delete + 1
            else:
                final = final.append(ranks.iloc[i,:])

            # print("Variant " + str(i + 1) + " out of " + str(ranks.shape[0]) + " processed. Deleted " + str(delete) + " out of " + str(ranks.shape[0]) ,end='\r');
            self.update_state(state='PROGRESS', meta={'current': 5 + which_file*90/num_files + i*90/(num_files * ranks_shape), 'total': 100, 'status': 'Another variant processed.'})

        # print("\n")
        final = final[ranks.columns]

        self.update_state(state='PROGRESS', meta={'current': 5 + (which_file + 1)*90/num_files, 'total': 100, 'status': 'Another variant processed.'})

        openme = open('res/README.txt', 'a')
        openme.write(file)
        openme.write("\nVariant " + str(i + 1) + " out of " + str(ranks.shape[0]) + " processed. Deleted " + str(delete) + " out of " + str(ranks.shape[0]) + "\n\n\n")
        openme.close()
        print(checksort)

        if checksort == 'true':
            print("Will try to sort. ")
            sort = final['Gene.refGene'].value_counts()
            order_genes = list(sort.keys())
            exclude_genes = list(sort[sort == 1].keys())

            ds = pd.DataFrame(columns=final.columns)
            length = len(order_genes)
            i = 0
            for gene in order_genes:
                i = i + 1
                print("Gene " + str(i) + " out of " + str(length) + " processed" ,end='\r')
                if gene not in exclude_genes:
                    ds = ds.append(final[final['Gene.refGene'] == gene])

            final = ds
            print("\n")

        blacklisted_result_files.append(tuple((file, final)))


    self.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Read all your files'})
    for pair in blacklisted_result_files:
        name = pair[0]
        df = pair[1]
        df.to_csv('res/' + name.rsplit('.',1)[0] + '_' + blacklist_file_name , index=None)

    return {'current':100, 'total':100, 'status': 'Task Completed!', 'result': 100}


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')




# 89888988898889888988898889888988898889888988898889888988898889888988898889888988898889888988898889888988898889888988898889888988898889888988898889888988898889888988898889888988898889888988898889888988898889888988898889888988898889
