import sys
import click

import numpy as np
import pandas as pd

import os, sys

from beaminfo.simple_query import query_full_day
from utils.dbmanager import add_day_pot_beam, create_connection, remove_day_pot_beam, remove_daily_collected_pot
from runinfo.read_run_info import insert_daily_runs, make_timestamp, get_day_range

# from plotting.plots_utils import makeCumulativePOTPlot

from plotting.plots_utils import potEfficiency, potCumulative, daqEfficiency, intensityAndCumulativePot, makeCumulativePOTPlot

USER = os.environ['USER']
potDir = os.environ['potDir']

masterDBName = "RunSummary.db"

sys.path.append(potDir)

#######################################################################################################

@click.group("pot_evaluation")
@click.pass_context
def cli(ctx):
    '''
    POT Evaluation commands

    '''

#######################################################################################################

@cli.command("update-daily-pot")
@click.argument("start_day")
@click.argument("end_day")
@click.argument("override")
@click.pass_context
def update_daily_pot( ctx, start_day="", end_day="", override=False ):
    """
    Update the delivered POT for both beam: 
    Args: 
        start_day : string with the day with the values to update in the format "yyyy-mm-dd"
        end_dat : string with the day with the values to update in the format "yyyy-mm-dd"
        override: delete if a row for that day already exists 
    Returs: 
        None
    """

    print("@@ Connecting to %s/dbase/%s"%(potDir,masterDBName))
    conn = create_connection("%s/dbase/%s"%(potDir,masterDBName))

    if conn is not None:

        print( "Updating the POT delivered between : {} ~ {}".format(start_day,end_day) )

        days = get_day_range(start_day,end_day)
        for day in days:
          if override:
              print( "Remove existing rows with key on: {}".format(day) )

              remove_day_pot_beam(conn, day, "bnb")
              remove_day_pot_beam(conn, day, "numi")
          
          ts_start_day = make_timestamp( day+" 00:00:00 CDT", "%Y-%m-%d %H:%M:%S %Z" )
          ts_end_day   = make_timestamp( day+" 23:59:59 CDT", "%Y-%m-%d %H:%M:%S %Z" )

          numi_beam_info = query_full_day(ts_start_day,ts_end_day, "numi")
          bnb_beam_info = query_full_day(ts_start_day,ts_end_day, "bnb")

          add_day_pot_beam( conn, ( day, numi_beam_info[0], numi_beam_info[1], numi_beam_info[2]), "numi" )
          add_day_pot_beam( conn, ( day, bnb_beam_info[0], bnb_beam_info[1], bnb_beam_info[2]), "bnb")

          #add_day_beam_info( conn, day, ts_start_day, ts_end_day, "numi" )
          
          print(" ALL pot delivered information updated for day {} ".format(day))
         
    else:

      print("FAILED CONNECTION")


#######################################################################################################

@cli.command("update-daily-runs")
@click.argument("start_day")
@click.argument("end_day")
@click.argument("override")
@click.pass_context
def update_daily_runs( ctx, start_day="", end_day="", override=False ):
    """
    Update the collected POT associated to a run for both beam: 
    Args: 
        day: string with the day with the values to update in the format "yyyy-mm-dd"
        override: delete if a row for that day already exists 
    Returs: 
        None
    """

    conn = create_connection("%s/dbase/%s"%(potDir, masterDBName))

    if conn is not None:

        print( "@@ Updating the POT collected between : {} ~ {}".format(start_day,end_day) )

        days = get_day_range(start_day,end_day)
        for day in days:
          if override:
            print( "Remove existing rows with key on: {}".format(day) )
            remove_daily_collected_pot( conn, day )

          insert_daily_runs( conn, day )
        print( "@@ -> ALL pot collected information updated between : {} ~ {}".format(start_day,end_day) )

    else:

        print("FAILED CONNECTION")

#######################################################################################################

@cli.command("make-daq-plots")
@click.pass_context
@click.argument("start_day")
@click.argument("end_day")
def make_daq_plots( ctx, start_day="", end_day="" ):
    """
    Make the daq plots with the new day information
    """

    if start_day=="":
        start_day="2021-05-31"
    if end_day=="":
        end_day=today.strftime("%Y-%m-%d")

    time_range = (start_day, end_day)

    print("Potting between {} and {}".format(start_day, end_day) )

    conn = create_connection("%s/dbase/%s"%(potDir, masterDBName))

    if conn is None:
        print("FAILED CONNECTION")
    
    pot_run_collected = pd.read_sql( "SELECT * from daily_collected_pot", conn )
    pot_daily_bnb = pd.read_sql( "SELECT * from day_pot_bnb", conn )
    pot_daily_numi = pd.read_sql( "SELECT * from day_pot_numi", conn )
    
    conn.close()

    # Merge BNB
    pot_run_collected = pot_run_collected.join( pot_daily_bnb.set_index("day"), on="day" ) 
    pot_run_collected.rename( columns={ "pot" : "pot_bnb_delivered"}, inplace=True )
    pot_run_collected.rename( columns={ "spill" : "spill_bnb_delivered"}, inplace=True )
    pot_run_collected.rename( columns={ "mode" : "mode_bnb"}, inplace=True )
    # Merge Numi
    pot_run_collected = pot_run_collected.join( pot_daily_numi.set_index("day"), on="day" ) 
    pot_run_collected.rename( columns={ "pot" : "pot_numi_delivered"}, inplace=True )
    pot_run_collected.rename( columns={ "spill" : "spill_numi_delivered"}, inplace=True )
    pot_run_collected.rename( columns={ "mode" : "mode_numi"}, inplace=True )

    pot_run_collected["ratio_bnb"] = pot_run_collected["pot_bnb_collected"] / pot_run_collected["pot_bnb_delivered"]
    pot_run_collected["ratio_numi"] = pot_run_collected["pot_numi_collected"] / pot_run_collected["pot_numi_delivered"]

    pot_run_collected["bnb_intensity"] = pot_run_collected["pot_bnb_delivered"]/ pot_run_collected["spill_bnb_delivered"]*1E12
    pot_run_collected["numi_intensity"] = pot_run_collected["pot_numi_delivered"]/ pot_run_collected["spill_numi_delivered"]*1E12

    pot_run_collected = pot_run_collected.sort_values('day')
    pot_run_collected_alltime = pot_run_collected

    ## strip df by time range

    pot_run_collected = pot_run_collected[ pd.to_datetime( pot_run_collected['day'] ) >= pd.to_datetime( start_day ) ]
    pot_run_collected = pot_run_collected[ pd.to_datetime( pot_run_collected['day'] ) <= pd.to_datetime( end_day ) ]

    ## Print final DataGrame

    print(pot_run_collected)

    ## Median

    print("@@ Medians")

    print("pot_bnb_collected = ",  np.median(pot_run_collected["pot_bnb_collected"]) )
    print("pot_numi_collected = ", np.median(pot_run_collected["pot_numi_collected"]) )

    print("pot_bnb_delivered = ",  np.median(pot_run_collected["pot_bnb_delivered"]) )
    print("pot_numi_delivered = ", np.median(pot_run_collected["pot_numi_delivered"]) )

    print("ratio_bnb = ",  np.median(pot_run_collected["ratio_bnb"]) )
    print("ratio_numi = ", np.median(pot_run_collected["ratio_numi"]) )
    print("runtime = ",  np.median(pot_run_collected["runtime"]) )

    ## Sum

    print("@@ Sum")

    print("BNB")
    print("- Delivered = %1.2e POT, %d spills"%(np.sum(pot_run_collected["pot_bnb_delivered"])*1E12, np.sum(pot_run_collected["spill_bnb_delivered"])) )
    print("- Collected = %1.2e POT, %d spills"%(np.sum(pot_run_collected["pot_bnb_collected"])*1E12, np.sum(pot_run_collected["spill_bnb_collected"])) )
    print("- Collected/Delivered = %1.3f"%(np.sum(pot_run_collected["pot_bnb_collected"])/np.sum(pot_run_collected["pot_bnb_delivered"])) )
    print("NuMI")
    print("- Delivered = %1.2e POT, %d spills"%(np.sum(pot_run_collected["pot_numi_delivered"])*1E12, np.sum(pot_run_collected["spill_numi_delivered"])) )
    print("- Collected = %1.2e POT, %d spills"%(np.sum(pot_run_collected["pot_numi_collected"])*1E12, np.sum(pot_run_collected["spill_numi_collected"])) )
    print("- Collected/Delivered = %1.3f"%(np.sum(pot_run_collected["pot_numi_collected"])/np.sum(pot_run_collected["pot_numi_delivered"])) )
    sumRunTime = np.sum(pot_run_collected["runtime"])
    print("Runtime = %d sec"%( int(sumRunTime) ) )
    print("        = %1.1f hrs"%( sumRunTime/3600. ) )
    print("        = %1.1f days"%( sumRunTime/3600./24. ) )

    # MAKE PLOTS, SAVE THEM 
    potEfficiency(pot_run_collected, "bnb", time_range)\
        .savefig("fig/eff_pot_bnb.pdf")
    
    potEfficiency(pot_run_collected, "numi", time_range)\
        .savefig("fig/eff_pot_numi.pdf")
    
    potCumulative(pot_run_collected, ["numi", "bnb"], time_range)\
        .savefig("fig/cumulative_pot_numi_bnb.pdf")
    
    potCumulative(pot_run_collected, ["numi"], time_range)\
        .savefig("fig/cumulative_pot_numi.pdf")
    
    potCumulative(pot_run_collected, ["bnb"], time_range)\
        .savefig("fig/cumulative_pot_bnb.pdf")

    daqEfficiency( pot_run_collected, time_range )\
        .savefig("fig/eff_daq_numi_bnb.pdf")
    
    intensityAndCumulativePot( pot_run_collected, "bnb", time_range)\
        .savefig("fig/intensity_and_cumulative_pot_bnb.pdf")

    intensityAndCumulativePot( pot_run_collected, "numi", time_range)\
        .savefig("fig/intensity_and_cumulative_pot_numi.pdf")


    startDay, endDay = time_range

    makeCumulativePOTPlot( 
        pot_run_collected_alltime, 
        ('2022-06-09', '2022-07-09'), 
        ('2022-12-20', '2023-07-14'), 
        ('2024-03-14', '2024-07-10'), 
        ('2024-12-10', '2025-07-07'),
        ('2025-10-16', endDay) 
    )\
        .savefig(f"fig/collected_both_up_to{endDay}.pdf")
    
    return

#######################################################################################################

# @cli.command("make-runbyrun-plots")
# @click.pass_context
# @click.argument("run")

# def make_runbyrun_plots( ctx, run=""):
#     """
#     Make the daq plots with the new day information
#     TODO: select range
#     """
#     conn = create_connection("%s/dbase/run02_beaminfo.db"%(potDir))

#     if conn is None:
#         print("FAILED CONNECTION")
    
#     pot_daily_run=pd.read_sql( "SELECT * from run_day_pot", conn )
#     pot_run_=pd.read_sql( "SELECT * from run_pot", conn )

#     pot_run.to_csv('dumpbnb.csv')
#     conn.close()

#     # DB Manipulation
#     pot_run_collected = pd.DataFrame(pot_run)
#     print(pot_run_collected[1]) 
    
#     return

def main():
    cli(obj=dict())


if '__main__' == __name__:
    main()
