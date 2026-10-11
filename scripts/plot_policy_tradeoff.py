"""Regenerate a shareable figure from measured frozen evaluation data."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['svg.fonttype']='none'

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',default='benchmarks/diagnostic-final.json');p.add_argument('--out',default='benchmarks/policy-tradeoff.svg');a=p.parse_args();d=json.loads(Path(a.input).read_bytes());fig,(ax,bx)=plt.subplots(1,2,figsize=(12,5),gridspec_kw={'width_ratios':[1.5,1]})
    colors={'fixed':'#526982','threshold':'#8f784d','random':'#9b636b','evidence':'#7472a0','phase':'#007e82'}
    for name,s in d['policies'].items():
        r=s['accuracy'];ax.errorbar(s['shots']/1000,100*r['rate'],yerr=[[100*(r['rate']-r['low'])],[100*(r['high']-r['rate'])]],fmt='o',capsize=4,color=colors[name]);ax.annotate(name,(s['shots']/1000,100*r['rate']),xytext=(7,12 if name=='evidence' else -14 if name=='threshold' else 0),textcoords='offset points',va='center',color=colors[name])
    ax.set(xlabel='Actual total shots (thousands; 68 cases / policy)',ylabel='Correct category (%)',ylim=(10,105),xlim=(260,540),title='Accuracy and measurement cost');ax.grid(alpha=.2)
    names=list(d['policies']);bars=bx.barh(names,[d['policies'][n]['evaluations'] for n in names],color=[colors[n] for n in names]);bx.bar_label(bars,padding=3);bx.set(xlabel='Total local circuit evaluations',xlim=(0,380),title='Sampled and exact-state evaluations');bx.spines[['top','right']].set_visible(False)
    fig.suptitle('QFAULT frozen simulation holdout: quality costs more measurements',fontweight='bold');fig.text(.03,.025,'Wilson 95% intervals are descriptive. Equal ceilings: 8,192 shots and 6 evaluations / case.\nPhase policy misses two QFT angle faults; exact-state attribution is privileged simulation.',fontsize=9);fig.tight_layout(rect=(0,.10,1,.93));out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out);
    if out.suffix=='.svg': out.write_text('\n'.join(line.rstrip() for line in out.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8')
    fig.savefig(out.with_suffix('.png'),dpi=160);print('Saved',out,'using Matplotlib',matplotlib.__version__)
if __name__=='__main__':main()
