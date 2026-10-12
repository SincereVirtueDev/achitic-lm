import json,argparse
from pathlib import Path
import torch
from torch.nn import functional as F
from .model import AchiticLM,Config
from .tokenizer import Tokenizer

def sequence_logprob(model,prompt,response,pad=-100):
    # Response-only log probability, conditioned on the prompt.
    ids=torch.tensor([prompt+response],device=next(model.parameters()).device)
    if len(prompt)<1 or len(ids[0])>model.config.context:raise ValueError('invalid sequence length')
    logits,_=model(ids[:,:-1]); targets=ids[:,1:]
    lp=F.log_softmax(logits.float(),dim=-1).gather(-1,targets.unsqueeze(-1)).squeeze(-1)
    return lp[:,len(prompt)-1:].sum(-1)

def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['sft','dpo'],required=True)
    p.add_argument('--checkpoint',required=True);p.add_argument('--tokenizer',required=True)
    p.add_argument('--data',required=True);p.add_argument('--out',required=True)
    p.add_argument('--steps',type=int,default=100);p.add_argument('--lr',type=float,default=1e-5)
    p.add_argument('--beta',type=float,default=0.1);a=p.parse_args()
    ck=torch.load(a.checkpoint,map_location='cpu',weights_only=False);cfg=Config(**ck['config'])
    device='cuda' if torch.cuda.is_available() else 'cpu';model=AchiticLM(cfg).to(device)
    model.load_state_dict(ck['model']);model.train();tok=Tokenizer(a.tokenizer)
    ref=None
    if a.mode=='dpo':
        ref=AchiticLM(cfg).to(device);ref.load_state_dict(ck['model']);ref.eval()
        for par in ref.parameters():par.requires_grad_(False)
    rows=[json.loads(s) for s in Path(a.data).read_text().splitlines() if s.strip()]
    opt=torch.optim.AdamW(model.parameters(),lr=a.lr)
    for i in range(a.steps):
        row=rows[i%len(rows)];prompt=tok.encode(row['prompt'],add_bos=True)
        if a.mode=='sft':
            response=tok.encode(row['response'],add_eos=True)
            ids=(prompt+response)[:cfg.context]
            if len(ids)<=len(prompt):continue
            x=torch.tensor([ids[:-1]],device=device)
            y=torch.tensor([ids[1:]],device=device)
            y[:,:len(prompt)-1]=-100
            _,loss=model(x,y)
        else:
            good=tok.encode(row['chosen'],add_eos=True);bad=tok.encode(row['rejected'],add_eos=True)
            if max(len(prompt)+len(good),len(prompt)+len(bad))>cfg.context:continue
            chosen=sequence_logprob(model,prompt,good);rejected=sequence_logprob(model,prompt,bad)
            with torch.no_grad():
                rc=sequence_logprob(ref,prompt,good);rr=sequence_logprob(ref,prompt,bad)
            loss=-F.logsigmoid(a.beta*((chosen-rejected)-(rc-rr))).mean()
        opt.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.0);opt.step()
        if i%10==0:print(i,float(loss.detach()))
    torch.save({'model':model.cpu().state_dict(),'config':vars(cfg),'stage':a.mode},a.out)
if __name__=='__main__':main()
