import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import pandas as pd
import numpy as np

from statistics import mode
from datetime import timedelta

beam_name = {
   'bnb': 'BNB',
   'numi': 'NuMI'
}

import mplhep as hep

plt.style.use(hep.style.DUNE)
plt.rcParams['font.size'] = 15

def potEfficiency(df: pd.DataFrame, beam: str, range):

  fig, axs = plt.subplots(figsize=(8, 5.5), nrows=2, height_ratios=[6, 2], sharex=True)
  fig.subplots_adjust(hspace=0.1)
  ax0, ax1 = axs
  
  # ax0.set_title(beam_name[beam], fontsize=18, loc='left')
  hep.label.exp_text(beam_name[beam], 'Collected/Delivered POT', ax=ax0)

  ax0.yaxis.grid(linestyle='dashed')
  
  x = pd.to_datetime(df['day'], utc=True)
  y = df[f'pot_{beam}_delivered']/1000000
  ax0.bar(x, y, align='center', width=1.0, label='Delivered', alpha=0.4)
  ax0.set_ylim(0., 1.3*y.max())

  y=df[f'pot_{beam}_collected']/1000000
  ax0.bar(x, y, align='center', width=1.0, label='Collected', alpha=0.6)

  ax0.set_ylabel('$10^{18}$ POT/day', fontsize=16)

  ax0.set_xlim( pd.to_datetime(range[0], utc=True) - timedelta(days=0.5), pd.to_datetime(range[1], utc=True) + timedelta(days=0.5) )

  ax0.legend(fontsize=17, edgecolor='none', ncols=2)
    
  ax1.plot(x, df[f'ratio_{beam}'], 'o', color='black', markersize=10, markerfacecolor='gray', markeredgecolor='black', markeredgewidth=2)

  if len(x) <= 10:
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
  ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y, %a'))
  ax1.tick_params(axis='x', rotation=25)
  plt.setp(ax1.get_xticklabels(), ha='right')

  ax1.set_ylabel('Ratio', fontsize=16)
  ax1.set_yticks([0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9], minor=True)
  ax1.yaxis.grid(linestyle='dashed', which='major')
  ax1.set_ylim(-0.1, 1.1)
  fig.tight_layout()
  
  return fig

def potCumulative(df: pd.DataFrame, beams: list[str], range):

  fig, ax0 = plt.subplots(figsize=(8, 5.5))

  df["timeindex"] = pd.to_datetime( df["day"], utc=True )
  df = df[(df.timeindex >= pd.to_datetime(range[0], utc=True)) & (df.timeindex <= pd.to_datetime(range[1], utc=True))]

  x = df["timeindex"].values

  for i, beam in enumerate(beams):

    y=np.cumsum(df[f'pot_{beam}_delivered']/1000000)
    ax0.plot(x, y, (f':C{i}' if len(beams) > 1 else '-'), 
             linewidth=4, label=f'{beam_name[beam]} Delivered ${np.max(y):.1f} \\times 10^{{18}}$ POT')

    y=np.cumsum( df[f'pot_{beam}_collected']/1000000)
    ax0.plot(x, y, (f'C{i}' if len(beams) > 1 else '-'), 
             linewidth=4, label=f'{beam_name[beam]} Collected ${np.max(y):.1f} \\times 10^{{18}}$ POT')

  ax0.set_ylabel('$10^{18}$ POT', fontsize=16)
  ax0.set_xlabel('Day (UTC)', fontsize=16)

  if len(x)<=10:
    ax0.xaxis.set_major_locator(mdates.DayLocator(interval=1))
  ax0.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y, %a'))
  ax0.tick_params(axis='x', rotation=25)
  plt.setp(ax0.get_xticklabels(), ha='right')

  ax0.legend(fontsize=17)

  ax0.set_xlim(pd.to_datetime(range[0], utc=True), pd.to_datetime(range[1], utc=True))
  fig.tight_layout()

  return fig

def daqEfficiency(pot_daily_collected, range):

  fig, ax = plt.subplots(figsize=(8, 5.5))
  start, end = range

  norm=3600.*24.

  ax.plot(
      pd.to_datetime(pot_daily_collected['day'], utc=True), 
      pot_daily_collected['runtime']/norm, 
      '-.', linewidth=5, label='DAQ Uptime')

  nDays = (pd.to_datetime(end, utc=True ) - pd.to_datetime(start, utc=True )).days + 1
  totalRunTime = np.sum(pot_daily_collected['runtime'])/norm
    
  print('@@ DAQ efficiency')
  print(f'- Number of days between {start} and {end} = {nDays}')
  print(f'- Total run time in this period = {totalRunTime:1.2f} days')
  print(f'- DAQ efficiency = (DAQ running time)/(Time interval) = {totalRunTime/float(nDays):1.3f}')
  
  ax.yaxis.grid(True, linestyle='dashed')

  ax.set_ylim((0.0, 1.1))
  ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y, %a'))
  ax.tick_params(axis='x', rotation=25)
  plt.setp(ax.get_xticklabels(), ha='right')
# # Optional: Ensure labels are aligned correctly
# p
  ax.set_ylabel('DAQ Time / 24 hours', fontsize=16)

  ax1 = ax.twinx()

  ax1.plot(
    pd.to_datetime(pot_daily_collected['day'], utc=True), 
    pot_daily_collected['ratio_bnb'], 
    'o', markersize=14, markerfacecolor='#9EDE73', 
    markeredgecolor='black', markeredgewidth=2, 
    label='BNB Efficiency'
  )
  ax1.plot(
    pd.to_datetime(pot_daily_collected['day'], utc=True), 
    pot_daily_collected['ratio_numi'], 
    '^', markersize=14, markerfacecolor='#BE0000', 
    markeredgecolor='black', markeredgewidth=2,
    label='NuMI Efficiency'
  )

  ax1.set_ylim((0.0, 1.1))
  ax1.set_ylabel('POT collected / POT delivered', fontsize=16)
  ax1.set_xlabel('Day (UTC)', fontsize=16)

  ax.legend(fontsize=17)

  ax.set_xlim(pd.to_datetime(start, utc=True), pd.to_datetime(end, utc=True))
  fig.tight_layout()

  return fig

def intensityAndCumulativePot(df, beam, range):

  fig, ax0 = plt.subplots(figsize=(8, 5.5))
  start, stop = range

  df['timeindex'] = pd.to_datetime(df['day'], utc=True)
  df = df[(df.timeindex >= pd.to_datetime(start, utc=True)) & (df.timeindex <= pd.to_datetime(stop, utc=True))]
  x = df['timeindex'].values

  hep.label.exp_text(beam_name[beam], 'Beam intensity/POT')

  beamNormPower = 12 if beam == 'bnb' else 13
  y = df[f'{beam}_intensity']/10**beamNormPower

  ax0.plot(
    x, y,
    label=f'Intensity\n(${np.mean(y):1.2f} \\times 10^{{{beamNormPower}}}$ POT/spill)',
    linewidth=3, linestyle='--'
  )

  if beam == 'bnb':
    ax0.set_ylim((0.0, 6.0))
  if beam == "numi":
    ax0.set_ylim((0.0, 8.0))
  
  ax0.set_ylabel(f'Intensity ($\\times 10^{{{beamNormPower}}}$ POT/spill)', fontsize=16)

  ax1 = ax0.twinx()

  y = np.cumsum(df[f'pot_{beam}_delivered']/1000000)
  ax1.plot( x, y, linewidth=4.0, label=f'Delivered ${np.max(y):.1f} \\times 10^{{18}}$ POT', color='C1')

  y = np.cumsum(df[f'pot_{beam}_collected']/1000000)
  ax1.plot( x, y, linewidth=4.0, label=f'Collected ${np.max(y):.1f} \\times 10^{{18}}$ POT', color='C2')

  ax1.set_ylabel('$\\times 10^{18}$ POT', fontsize=16)
  ax1.set_xlabel('Day (UTC)', fontsize=16)
  ax0.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y, %a'))
  ax0.tick_params(axis='x', rotation=25)
  plt.setp(ax0.get_xticklabels(), ha='right')
  ax0.set_xlim(pd.to_datetime(start, utc=True), pd.to_datetime(stop, utc=True))
  ax0.legend(fontsize=17, loc='upper left')
  ax1.legend(fontsize=17, loc='lower right')

  fig.tight_layout()
  
  return fig

# def makePOTPlotRun( df, beam, run ):

#     fig=plt.figure( figsize=(15,5) )

#     gs=GridSpec(2,1, height_ratios=[6, 2]) 

#     ## The pot plots ####################################################

#     ax0=fig.add_subplot(gs[0]) # First row, first column
    
#     ax0.set_title(beam, fontsize=18)

#     #ax0.axis("off")
#     ax0.spines["right"].set_visible(False)
#     ax0.spines["left"].set_visible(False)
#     ax0.spines["top"].set_visible(False)

#     ax0.yaxis.grid( linestyle='-' )
    
#     del_label="pot_%s_delivered" % beam
    
#     x=pd.to_datetime( df["day"], utc=True )
#     y=df[del_label]/1000000
#     ax0.fill_between(x, y, step="mid", alpha=0.2)
#     ax0.step( x, y, drawstyle="steps", where='mid', linewidth=2.0, label="Delivered" )
    
#     col_label="pot_%s_collected" % beam
    
#     y=df[col_label]/1000000
#     ax0.fill_between(x, y, step="mid", alpha=0.4)
#     ax0.step( x, y, drawstyle="steps", where='mid', linewidth=2.0,label="Collected" )

#     ax0.set_ylabel( "$10^{18}$ POT/day", fontsize=16 )

#     ax0.tick_params(axis="x",direction="in", bottom="on")

#     ax0.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y, %a'))

#     ax0.set_xlim( pd.to_datetime( range[0], utc=True ), pd.to_datetime( range[1], utc=True ) )

#     fig.legend(fontsize=17fontsize=18)

#     ## The ratio below ######################################################

#     ax1=fig.add_subplot(gs[1]) # First row, second column
    
#     ratio_label="ratio_%s" % beam
    
#     ax1.plot(x, df[ratio_label], 'o', color='black', markersize=10, markerfacecolor='gray', markeredgecolor='black', markeredgewidth=2)
#     ax1.set_ylabel( "Ratio", fontsize=16 )

#     #ax0.grid(True, linestyle='--')
#     ax1.tick_params(axis="y",direction="in", left="on", right='on')
#     ax1.tick_params(axis="x",direction="in", bottom="on",top='on')
#     ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y, %a'))
    
#     ax1.set_xlim( pd.to_datetime( range[0], utc=True ), pd.to_datetime( range[1], utc=True ) )

#     ax1.set_ylim(0, 1.0)
    
#     plt.tight_layout()
    
#     return plt

# def makePOTPlotBothRun( df, beam1, beam2, run ):

#     fig=plt.figure( figsize=(8, 5.5) )

#     gs=GridSpec(2,1, height_ratios=[6, 2])

#     ## The pot plots ####################################################

#     ax0=fig.add_subplot(gs[0]) # First row, first column

#     ax0.set_title(beam1.upper(), fontsize=18)

#     del_label1="pot_%s_delivered" % beam1
 
#     df["timeindex"] = pd.to_datetime( df["day"], utc=True )
#     df = df[ ( df.timeindex >= pd.to_datetime( range[0], utc=True ) ) & ( df.timeindex <= pd.to_datetime( range[1], utc=True ) ) ]

#     x=df["timeindex"].values
#     y=np.cumsum(df[del_label1]/1000000)

#     ax0.plot( x, y,':C0', linewidth=4.0, label="NuMI Delivered $%.1f \\times 10^{18}$ POT" % np.max(y))

#     del_label2="pot_%s_delivered" % beam2

#     y=np.cumsum(df[del_label2]/1000000)

#     ax0.plot( x, y, ':C1', linewidth=4.0, label="BNB Delivered $%.1f \\times 10^{18}$ POT" % np.max(y))

#     col_label1="pot_%s_collected" % beam1

#     y=np.cumsum( df[col_label1]/1000000 )
#     ax0.plot( x, y, linewidth=4.0,label="NuMI Collected $%.1f \\times 10^{18}$ POT" % np.max(y) )

#     col_label2="pot_%s_collected" % beam2

#     y=np.cumsum( df[col_label2]/1000000 )
#     ax0.plot( x, y, linewidth=4.0,label="BNB Collected $%.1f \\times 10^{18}$ POT" % np.max(y) )

#     ax0.set_ylabel( "$10^{18}$ POT", fontsize=16 )
#     ax0.set_xlabel( "Day (UTC)", fontsize=16 )

#     ax0.tick_params(axis="x",direction="in", bottom="on")

#     ax0.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y, %a'))

#     ax0.legend(fontsize=17fontsize=18, loc='upper left')

#     ax0.set_xlim( pd.to_datetime( range[0], utc=True ), pd.to_datetime( range[1], utc=True ) )


#     plt.tight_layout()

#     return plt

# def makePOTSumPlotRun( df, beam, run ):

#     fig=plt.figure( figsize=(8, 5.5) )

#     gs=GridSpec(2,1, height_ratios=[6, 2]) 

#     ## The pot plots ####################################################

#     ax0=fig.add_subplot(gs[0]) # First row, first column
    
#     ax0.set_title(beam.upper(), fontsize=18)
    
#     del_label="pot_%s_delivered" % beam
    
#     df["timeindex"] = pd.to_datetime( df["day"], utc=True )
#     df = df[ ( df.timeindex >= pd.to_datetime( range[0], utc=True ) ) & ( df.timeindex <= pd.to_datetime( range[1], utc=True ) ) ]    

#     x=df["timeindex"].values
#     y=np.cumsum(df[del_label]/1000000)
    
#     ax0.plot( x, y, linewidth=4.0, label="Delivered $%.1f \\times 10^{18}$ POT" % np.max(y) )
    
#     col_label="pot_%s_collected" % beam
    
#     y=np.cumsum( df[col_label]/1000000 )
#     ax0.plot( x, y, linewidth=4.0,label="Collected $%.1f \\times 10^{18}$ POT" % np.max(y) )

#     ax0.set_ylabel( "$10^{18}$ POT", fontsize=16 )
#     ax0.set_xlabel( "Day (UTC)", fontsize=16 )
    
#     ax0.tick_params(axis="x",direction="in", bottom="on")

#     ax0.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y, %a'))

#     ax0.legend(fontsize=17fontsize=18, loc='upper left')

#     ax0.set_xlim( pd.to_datetime( range[0], utc=True ), pd.to_datetime( range[1], utc=True ) )


#     plt.tight_layout()
    
#     return plt


# def makeDAQEffPlotRun( pot_daily_collected, run ):

#     fig, ax = plt.subplots( 1,1, figsize=(18, 4.3), sharey=True )

#     norm=24

#     ax.plot( pd.to_datetime(pot_daily_collected["day"], utc=True), pot_daily_collected["runtime"]/(3600.)/norm, '-.', color="#E48900", linewidth=5, label="DAQ Uptime")

#     print( mode( pot_daily_collected["runtime"]/(3600.)) )
#     print( np.median( pot_daily_collected["runtime"]/(3600.)/norm) )
#     print( np.mean( pot_daily_collected["runtime"]/(3600.)) )
    
#     ax.yaxis.grid(True, linestyle='--')

#     ax.tick_params(axis="y",direction="in", left="on", right='on')
#     ax.tick_params(axis="x",direction="in", bottom="on",top='on')
#     ax.set_ylim((0.0, 1.1))
#     ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
#     ax.set_ylabel( "DAQ Time / 24 hours", fontsize=16 )

#     ax1 = ax.twinx()

#     #print ( pot_daily_collected["ratio_bnb"])
#     #print ( pot_daily_collected["ratio_numi"])

#     ax1.plot( pd.to_datetime(pot_daily_collected["day"], utc=True), pot_daily_collected["ratio_bnb"], 'o', markersize=14, markerfacecolor='#9EDE73', markeredgecolor='black', markeredgewidth=2, label="BNB Efficiency")
#     ax1.plot( pd.to_datetime(pot_daily_collected["day"], utc=True), pot_daily_collected["ratio_numi"], '^', markersize=14, markerfacecolor='#BE0000', markeredgecolor='black', markeredgewidth=2, label="NuMI Efficiency")
#     ax1.set_ylim((0.0, 1.1))
#     ax1.set_ylabel( "POT collected / POT delivered", fontsize=16 )
#     ax1.set_xlabel( "Day (UTC)", fontsize=16 )

#     fig.legend(fontsize=17fontsize=16, bbox_to_anchor=[0.2, 0.4])

#     ax.set_xlim( pd.to_datetime( range[0], utc=True ), pd.to_datetime( range[1], utc=True ) )


#     fig.tight_layout()

#     return plt

# def makePOTPlotBothRunCollected( df, beam1, beam2, rrun1, rrun2, rrun3, rrun4, rrun5 ):

#     fig, ax0 = plt.subplots( 1,1, figsize=(8, 5.5), sharey=True )

#     ## The pot plots ####################################################

#     df["timeindex"] = pd.to_datetime( df["day"], utc=True )


#     _selNuMIRHC = (df.mode_numi == 'nubar') & ( df.timeindex > pd.to_datetime( rrun2[1], utc=True ) )
#     _selNuMIFHC = (df.mode_numi == 'nu') | ( df.timeindex <= pd.to_datetime( rrun2[1], utc=True ) )

#     df["pot_numi_rhc_collected"] = df['pot_numi_collected'].where(_selNuMIRHC,0)
#     df["pot_numi_rhc_delivered"] = df['pot_numi_delivered'].where(_selNuMIRHC,0)
#     df["pot_numi_fhc_collected"] = df['pot_numi_collected'].where(_selNuMIFHC,0)
#     df["pot_numi_fhc_delivered"] = df['pot_numi_delivered'].where(_selNuMIFHC,0)


#     _selRUN1 = ( df.timeindex >= pd.to_datetime( rrun1[0], utc=True ) ) & ( df.timeindex <= pd.to_datetime( rrun1[1], utc=True ) )
#     _selRUN2 = ( df.timeindex >= pd.to_datetime( rrun2[0], utc=True ) ) & ( df.timeindex <= pd.to_datetime( rrun2[1], utc=True ) )
#     _selRUN3 = ( df.timeindex >= pd.to_datetime( rrun3[0], utc=True ) ) & ( df.timeindex <= pd.to_datetime( rrun3[1], utc=True ) )
#     _selRUN4 = ( df.timeindex >= pd.to_datetime( rrun4[0], utc=True ) ) & ( df.timeindex <= pd.to_datetime( rrun4[1], utc=True ) )
#     _selRUN5 = ( df.timeindex >= pd.to_datetime( rrun5[0], utc=True ) ) & ( df.timeindex <= pd.to_datetime( rrun5[1], utc=True ) )

#     # SELECT ONLY INSIDE THE THREE "RUN" PERIODS
#     df = df[ _selRUN1 | _selRUN2 | _selRUN3 | _selRUN4 | _selRUN5 ]


#     x=df["timeindex"].values

#     x=df["timeindex"].values

#     y=np.cumsum( df["pot_numi_delivered"]/100000000 )
#     ys = y
#     ax0.plot( x, y, ':C1', linewidth=4.0,linestyle='--',label="Total NuMI Delivered$%.2f \\times 10^{20}$ POT" % np.max(y) )
  
#     y=np.cumsum(df['pot_numi_collected']/100000000)
#     ys = np.append(ys,y)
#     ax0.plot( x, y, 'C0', linewidth=4.0, label="Total NuMI Collected$%.2f \\times 10^{20}$ POT" % np.max(y))

#     y=np.cumsum( df["pot_numi_rhc_collected"]/100000000 )
#     ys = np.append(ys,y)
#     ax0.plot( x, y, ':C0', linewidth=3.0,label="NuMI RHC$%.2f \\times 10^{20}$ POT" % np.max(y) )
  
#     y=np.cumsum( df["pot_numi_fhc_collected"]/100000000 )
#     ys = np.append(ys,y)
#     ax0.plot( x, y, "--C0", linewidth=3.0,label="NuMI FHC$%.2f \\times 10^{20}$ POT" % np.max(y) )


#     col_label2="pot_%s_collected" % beam2
#     y=np.cumsum( df[col_label2]/100000000 )
#     ax0.plot( x, y, 'C1', linewidth=4.0,label="BNB Collected $%.2f \\times 10^{20}$ POT" % np.max(y))

#     col_label1="pot_%s_collected" % beam1
#     y=np.cumsum( df[col_label1]/100000000 )
#     ax0.plot( x, y, 'C0', linewidth=4.0,label="NuMI Collected $%.2f \\times 10^{20}$ POT" % np.max(y))

#     df_rhc = df[df.mode_numi == 'nubar']
#     df_fhc = df[df.mode_numi == 'nu']

#     df_rhc = df_rhc[ ( df_rhc.timeindex >= pd.to_datetime( rrun1[0], utc=True ) ) & ( df_rhc.timeindex <= pd.to_datetime( rrun5[1], utc=True ) ) ]
#     x=df_rhc["timeindex"].values
#     y=np.cumsum( df_rhc[col_label1]/100000000 )
#     ax0.plot( x, y, ':C0', linewidth=4.0,label="NuMI RHC Collected $%.2f \\times 10^{20}$ POT" % np.max(y) )

#     df_fhc = df_fhc[ ( df_fhc.timeindex >= pd.to_datetime( rrun1[0], utc=True ) ) & ( df_fhc.timeindex <= pd.to_datetime( rrun5[1], utc=True ) ) ]
#     x=df_fhc["timeindex"].values
#     y=np.cumsum( df_fhc[col_label1]/100000000 )
#     ax0.plot( x, y, '--C0', linewidth=4.0,label="NuMI FHC Collected $%.2f \\times 10^{20}$ POT" % np.max(y) )


#     ax0.set_ylabel( "$10^{20}$ POT", fontsize=16 )
#     ax0.set_xlabel( "Day (UTC)", fontsize=16 )

#     ax0.tick_params(axis="x",direction="in", bottom="on")

#     ax0.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y, %a'))

#     ax0.legend(fontsize=17fontsize=18, loc='upper left', frameon=False)

#     ax0.set_xlim( pd.to_datetime( rrun1[0], utc=True ) - timedelta(days=15), pd.to_datetime( rrun5[1], utc=True ) + timedelta(days=15) )
#     ax0.grid(alpha=0.5,linestyle="dashed")

# # Run1 
#     ax0.axvline( x=pd.to_datetime(rrun1[0], utc=True), linestyle="dashed",color="black")
#     ax0.axvline( x=pd.to_datetime(rrun1[1], utc=True), linestyle="dashed",color="black")
#     ax0.text(x=pd.to_datetime(rrun1[0], utc=True) + timedelta(days=3), y=1, s='Start RUN-1', rotation=90, 
#              fontsize=12, va="bottom")
#     ax0.text(x=pd.to_datetime(rrun1[1], utc=True) + timedelta(days=3), y=1, s='End RUN-1', rotation=90,
#              fontsize=12, va="bottom")

#     # Run2 
#     ax0.axvline( x=pd.to_datetime(rrun2[0], utc=True), linestyle="dashed",color="black")
#     ax0.axvline( x=pd.to_datetime(rrun2[1], utc=True), linestyle="dashed",color="black")
#     ax0.text(x=pd.to_datetime(rrun2[0], utc=True) + timedelta(days=3), y=1, s='Start RUN-2', rotation=90,
#             fontsize=12, va="bottom")
#     ax0.text(x=pd.to_datetime(rrun2[1], utc=True) + timedelta(days=3), y=1, s='End RUN-2', rotation=90,
#             fontsize=12, va="bottom")

#     # Run3 
#     ax0.axvline( x=pd.to_datetime(rrun3[0], utc=True), linestyle="dashed",color="black")
#     ax0.axvline( x=pd.to_datetime(rrun3[1], utc=True), linestyle="dashed",color="black")
#     ax0.text(x=pd.to_datetime(rrun3[0], utc=True) + timedelta(days=3), y=1, s='Start RUN-3', rotation=90,
#              fontsize=12, va="bottom")
#     ax0.text(x=pd.to_datetime(rrun3[1], utc=True) + timedelta(days=3), y=1, s='End RUN-3', rotation=90,
#              fontsize=12, va="bottom")
    
#     # Run4
#     ax0.axvline( x=pd.to_datetime(rrun4[0], utc=True), linestyle="dashed",color="black")
#     ax0.axvline( x=pd.to_datetime(rrun4[1], utc=True), linestyle="dashed",color="black")
#     ax0.text(x=pd.to_datetime(rrun4[0], utc=True) + timedelta(days=3), y=1, s='Start RUN-4', rotation=90,
#              fontsize=12, va="bottom")
#     ax0.text(x=pd.to_datetime(rrun4[1], utc=True) + timedelta(days=3), y=1, s='End RUN-4', rotation=90,
#              fontsize=12, va="bottom")
    
#      # Run5
#     ax0.axvline( x=pd.to_datetime(rrun5[0], utc=True), linestyle="dashed",color="black")
#     # ax0.axvline( x=pd.to_datetime(rrun4[1], utc=True), linestyle="dashed",color="black")
#     ax0.text(x=pd.to_datetime(rrun5[0], utc=True) + timedelta(days=3), y=1, s='Start RUN-5', rotation=90,
#              fontsize=12, va="bottom")
#     # ax0.text(x=pd.to_datetime(rrun4[1], utc=True) + timedelta(days=3), y=1, s='End RUN-4', rotation=90,
#     #          fontsize=12, va="bottom")

#     plt.tight_layout()

#     return plt

# def makeCumulativePOTPlot( df, rrun1, rrun2, rrun3, rrun4, rrun5 ):

#     fig, ax0 = plt.subplots( 1,1, figsize=(8, 5.5), sharey=True )

#     df["timeindex"] = pd.to_datetime( df["day"], utc=True )

#     _selNuMIRHC = (df.mode_numi == 'nubar') & ( df.timeindex > pd.to_datetime( rrun2[1], utc=True ) )
#     _selNuMIFHC = (df.mode_numi == 'nu') | ( df.timeindex <= pd.to_datetime( rrun2[1], utc=True ) )

#     df["pot_numi_rhc_collected"] = df['pot_numi_collected'].where(_selNuMIRHC,0)
#     df["pot_numi_rhc_delivered"] = df['pot_numi_delivered'].where(_selNuMIRHC,0)
#     df["pot_numi_fhc_collected"] = df['pot_numi_collected'].where(_selNuMIFHC,0)
#     df["pot_numi_fhc_delivered"] = df['pot_numi_delivered'].where(_selNuMIFHC,0)

#     _selBNBRHC = (df.mode_bnb == 'nubar')
#     _selBNBFHC = (df.mode_bnb == 'nu')
#     _selValidBNB = _selBNBRHC | _selBNBFHC

#     _selRUN1 = ( df.timeindex >= pd.to_datetime( rrun1[0], utc=True ) ) & ( df.timeindex <= pd.to_datetime( rrun1[1], utc=True ) )
#     _selRUN2 = ( df.timeindex >= pd.to_datetime( rrun2[0], utc=True ) ) & ( df.timeindex <= pd.to_datetime( rrun2[1], utc=True ) )
#     _selRUN3 = ( df.timeindex >= pd.to_datetime( rrun3[0], utc=True ) ) & ( df.timeindex <= pd.to_datetime( rrun3[1], utc=True ) )
#     _selRUN4 = ( df.timeindex >= pd.to_datetime( rrun4[0], utc=True ) ) & ( df.timeindex <= pd.to_datetime( rrun4[1], utc=True ) )
#     _selRUN5 = ( df.timeindex >= pd.to_datetime( rrun5[0], utc=True ) ) & ( df.timeindex <= pd.to_datetime( rrun5[1], utc=True ) )

#     # SELECT ONLY INSIDE THE THREE "RUN" PERIODS
#     df = df[ _selRUN1 | _selRUN2 | _selRUN3 | _selRUN4 | _selRUN5 ]

#     x=df["timeindex"].values

#     y=np.cumsum(df['pot_bnb_collected']/100000000)
#     ys = y
#     ax0.plot( x, y,'C1', linewidth=4.0, label="Total BNB $%.2f \\times 10^{20}$ POT" % np.max(y))

#     y=np.cumsum(df['pot_numi_collected']/100000000)
#     ys = np.append(ys,y)
#     ax0.plot( x, y, 'C0', linewidth=4.0, label="Total NuMI $%.2f \\times 10^{20}$ POT" % np.max(y))

#     y=np.cumsum( df["pot_numi_rhc_collected"]/100000000 )
#     ys = np.append(ys,y)
#     ax0.plot( x, y, ':C0', linewidth=3.0,label="NuMI RHC $%.2f \\times 10^{20}$ POT" % np.max(y) )
  
#     y=np.cumsum( df["pot_numi_fhc_collected"]/100000000 )
#     ys = np.append(ys,y)
#     ax0.plot( x, y, "--C0", linewidth=3.0,label="NuMI FHC $%.2f \\times 10^{20}$ POT" % np.max(y) )

#     ax0.set_ylabel( "$10^{20}$ POT", fontsize=16 )
#     #ax0.set_xlabel( "Day (UTC)", fontsize=16 )

#     ax0.tick_params(axis="x",direction="in", bottom="on")

#     if len(x)<=10:
#       ax0.xaxis.set_major_locator(mdates.DayLocator(interval=1))
#     ax0.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

#     ax0.legend(fontsize=17fontsize=16, loc='upper left', edgecolor='none', facecolor='white', framealpha=0.8)

#     ax0.set_xlim( pd.to_datetime( rrun1[0], utc=True ) - timedelta(days=15), pd.to_datetime( rrun5[1], utc=True ) + timedelta(days=15) )
#     ax0.grid(alpha=0.5,linestyle="dashed")

#     # Run1 
#     ax0.axvline( x=pd.to_datetime(rrun1[0], utc=True), linestyle="dashed",color="black")
#     ax0.axvline( x=pd.to_datetime(rrun1[1], utc=True), linestyle="dashed",color="black")
#     ax0.text(x=pd.to_datetime(rrun1[0], utc=True) + timedelta(days=3), y=1.25, s='Start RUN-1', rotation=90, 
#              fontsize=12, va="bottom")
#     ax0.text(x=pd.to_datetime(rrun1[1], utc=True) + timedelta(days=3), y=1.25, s='End RUN-1', rotation=90,
#              fontsize=12, va="bottom")

#     # Run2 
#     ax0.axvline( x=pd.to_datetime(rrun2[0], utc=True), linestyle="dashed",color="black")
#     ax0.axvline( x=pd.to_datetime(rrun2[1], utc=True), linestyle="dashed",color="black")
#     ax0.text(x=pd.to_datetime(rrun2[0], utc=True) + timedelta(days=3), y=2.25, s='Start RUN-2', rotation=90,
#             fontsize=12, va="bottom")
#     ax0.text(x=pd.to_datetime(rrun2[1], utc=True) + timedelta(days=3), y=0.75, s='End RUN-2', rotation=90,
#             fontsize=12, va="bottom")

#     # Run3 
#     ax0.axvline( x=pd.to_datetime(rrun3[0], utc=True), linestyle="dashed",color="black")
#     ax0.axvline( x=pd.to_datetime(rrun3[1], utc=True), linestyle="dashed",color="black")
#     ax0.text(x=pd.to_datetime(rrun3[0], utc=True) + timedelta(days=3), y=4.25, s='Start RUN-3', rotation=90,
#              fontsize=12, va="bottom")
#     ax0.text(x=pd.to_datetime(rrun3[1], utc=True) + timedelta(days=3), y=4.25, s='End RUN-3', rotation=90,
#              fontsize=12, va="bottom")
    
#     # Run4
#     ax0.axvline( x=pd.to_datetime(rrun4[0], utc=True), linestyle="dashed",color="black")
#     ax0.axvline( x=pd.to_datetime(rrun4[1], utc=True), linestyle="dashed",color="black")
#     ax0.text(x=pd.to_datetime(rrun4[0], utc=True) + timedelta(days=3), y=0.75, s='Start RUN-4', rotation=90,
#              fontsize=12, va="bottom")
#     ax0.text(x=pd.to_datetime(rrun4[1], utc=True) + timedelta(days=3), y=0.75, s='End RUN-4', rotation=90,
#              fontsize=12, va="bottom")
    
#     # Run5
#     ax0.axvline( x=pd.to_datetime(rrun5[0], utc=True), linestyle="dashed",color="black")
#     # ax0.axvline( x=pd.to_datetime(rrun4[1], utc=True), linestyle="dashed",color="black")
#     ax0.text(x=pd.to_datetime(rrun5[0], utc=True) + timedelta(days=3), y=0.75, s='Start RUN-5', rotation=90,
#              fontsize=12, va="bottom")
#     # ax0.text(x=pd.to_datetime(rrun4[1], utc=True) + timedelta(days=3), y=1, s='End RUN-4', rotation=90,
#     #          fontsize=12, va="bottom")

#     plt.tight_layout()

#     print(df.head())

#     return plt