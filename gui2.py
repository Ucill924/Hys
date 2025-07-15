_P='Status: Idle'
_O='0.000054'
_N='^0x[a-fA-F0-9]{40}$'
_M='0x... (Enter addresses here, one per line)'
_L='chainId'
_K='1.0'
_J='name'
_I='file'
_H='auto'
_G='readonly'
_F=None
_E='disabled'
_D='Error'
_C='normal'
_B='!disabled'
_A='#00ff00'
import tkinter as tk
from tkinter import ttk,filedialog,messagebox,scrolledtext
from tkinter.font import Font
from web3 import Web3
from eth_account import Account
from colorama import Fore,Style,init
import time,threading,re,json,os
init(autoreset=True)
def load_chains():
	'Load chain data from chains.json'
	try:
		with open('chains.json','r')as A:B=json.load(A)
		return B.get('evm_chains',[])
	except FileNotFoundError:messagebox.showerror(_D,'chains.json file not found.');return[]
	except json.JSONDecodeError:messagebox.showerror(_D,'Invalid JSON format in chains.json.');return[]
	except Exception as C:messagebox.showerror(_D,f"Error loading chains.json: {str(C)}");return[]
def load_receivers(source,is_file=True):
	'Load receiver addresses from a file or manual input';B=source
	try:
		if is_file:
			with open(B,'r')as E:C=[A.strip()for A in E if A.strip().startswith('0x')]
		else:C=[A.strip()for A in B.split('\n')if A.strip().startswith('0x')]
		D=[]
		for A in C:
			if re.match(_N,A):D.append(A)
			else:print(f"Invalid address skipped: {A}")
		return D
	except FileNotFoundError:return[]
	except Exception as F:print(f"Error loading receivers: {str(F)}");return[]
def generate_wallet():A=Account.create();return A.address,A.key.hex()
def save_wallet(index,address,private_key):
	with open('generated_wallets.txt','a')as A:A.write(f"U{index}: {address} | {private_key}\n")
def get_nonce(web3,address):
	try:return web3.eth.get_transaction_count(address,'pending')
	except Exception as A:print(f"Error fetching nonce: {str(A)}");return
def send_eth(web3,private_key,to_address,amount_wei,gas_limit,gas_price,chain_id,output_text,max_attempts=3):
	K='nonce';H=max_attempts;G=to_address;F=private_key;B=web3;A=output_text;E=Account.from_key(F);C=get_nonce(B,E.address)
	if C is _F:A.insert(tk.END,Fore.RED+f"❌ Failed to fetch nonce for {E.address}\n");return
	I={'to':G,'value':amount_wei,'gas':gas_limit,'gasPrice':gas_price,K:C,_L:chain_id}
	for L in range(H):
		try:
			M=B.eth.account.sign_transaction(I,F);D=B.eth.send_raw_transaction(M.raw_transaction);A.insert(tk.END,Fore.CYAN+f"🚀 TX Sent: {B.to_hex(D)} | ⏳ Waiting for confirmation...\n");A.see(tk.END);N=B.eth.wait_for_transaction_receipt(D,timeout=120)
			if N.status==1:A.insert(tk.END,Fore.GREEN+f"✅ TX Successful: {B.to_hex(D)}\n");A.see(tk.END);return D
			else:A.insert(tk.END,Fore.RED+f"❌ TX Failed (status 0): {B.to_hex(D)}\n");A.see(tk.END);return
		except Exception as J:
			A.insert(tk.END,Fore.YELLOW+f"⚠️ Attempt {L+1} failed: {str(J)}\n");A.see(tk.END)
			if'invalid nonce'in str(J).lower():
				C=get_nonce(B,E.address)
				if C is _F:A.insert(tk.END,Fore.RED+f"❌ Failed to fetch updated nonce for {E.address}\n");return
				I[K]=C
			time.sleep(5)
	A.insert(tk.END,Fore.RED+f"🚫 Failed to send to {G} after {H} attempts.\n");A.see(tk.END)
def run_transactions(rpc_url,chain_id,gas_price_gwei,amount_to_send_eth,private_key,receiver_source,is_file,return_wallet,output_text,status_label,start_button):
	S=private_key;N=chain_id;H=return_wallet;F='#ff0000';E='Status: Failed';C=start_button;B=status_label;A=output_text
	try:
		B.config(text='Status: Processing...',fg=_A);A.delete(1.,tk.END);D=Web3(Web3.HTTPProvider(rpc_url))
		if not D.is_connected():A.insert(tk.END,Fore.RED+'❌ Failed to connect to RPC.\n');B.config(text=E,fg=F);C.state([_B]);return
		I=21000;J=D.to_wei(gas_price_gwei,'gwei');X=D.to_wei(amount_to_send_eth,'ether');T=load_receivers(receiver_source,is_file)
		if not T:A.insert(tk.END,Fore.RED+'❌ No valid receiver addresses provided.\n');B.config(text=E,fg=F);C.state([_B]);return
		if not S:A.insert(tk.END,Fore.RED+'❌ Sender private key not provided.\n');B.config(text=E,fg=F);C.state([_B]);return
		if not re.match(_N,H):A.insert(tk.END,Fore.RED+'❌ Invalid return wallet address.\n');B.config(text=E,fg=F);C.state([_B]);return
		O=S;K=_F;P=_F
		for(G,U)in enumerate(T):
			A.insert(tk.END,Fore.MAGENTA+f"\n🎯 Step {G+1}: Generate Wallet U{G+1}\n");L,M=generate_wallet();save_wallet(G+1,L,M);Q=Account.from_key(O);R=D.eth.get_balance(Q.address);V=R-I*J*2
			if V<=0:A.insert(tk.END,Fore.RED+f"❌ Insufficient balance in {Q.address}\n");B.config(text=E,fg=F);C.state([_B]);return
			A.insert(tk.END,Fore.CYAN+f"📤 Transfer: {Q.address} → U{G+1} ({L})\n");Y=send_eth(D,O,L,V,I,J,N,A)
			if not Y:A.insert(tk.END,Fore.RED+'🛑 Stopping process due to failed transaction.\n');B.config(text=E,fg=F);C.state([_B]);return
			A.insert(tk.END,Fore.BLUE+f"📤 Transfer Fee: U{G+1} → Receiver {G+1}: {U}\n");Z=send_eth(D,M,U,X,I,J,N,A)
			if not Z:A.insert(tk.END,Fore.RED+'🛑 Stopping process due to failed transaction to receiver.\n');B.config(text=E,fg=F);C.state([_B]);return
			K=L;P=M;O=M;time.sleep(1)
		if K and P:
			A.insert(tk.END,Fore.MAGENTA+f"\n🎯 Sending remaining balance from {K} to return wallet: {H}\n");R=D.eth.get_balance(K);W=R-I*J
			if W>0:
				a=send_eth(D,P,H,W,I,J,N,A)
				if not a:A.insert(tk.END,Fore.RED+f"❌ Failed to send remaining balance to {H}\n")
				else:A.insert(tk.END,Fore.GREEN+f"✅ Remaining balance sent to {H}\n")
			else:A.insert(tk.END,Fore.YELLOW+f"⚠️ No remaining balance to send from {K}\n")
		A.insert(tk.END,Fore.GREEN+'\n✅ All transactions completed.\n');A.insert(tk.END,Fore.YELLOW+'🔐 Wallet data saved to: generated_wallets.txt\n');B.config(text='Status: Completed',fg=_A);C.state([_B])
	except Exception as b:A.insert(tk.END,Fore.RED+f"❌ Error: {str(b)}\n");B.config(text=E,fg=F);C.state([_B])
class EthereumGUI:
	def __init__(A,root):
		U='flat';T='manual';S='Manual';R='TFrame';Q='TCombobox';P='TRadiobutton';O='bold';N='Hide U Sybill';K='TButton';J='active';I='Courier New';H='#0a0a0a';G='#1c2526';D='e';C='w';A.root=root;A.root.title(N);A.root.geometry('700x650');A.root.configure(bg=H);E=ttk.Style();E.theme_use('clam');E.configure('TLabel',background=H,foreground=_A,font=(I,10));E.configure('TEntry',fieldbackground=G,foreground=_A,insertcolor=_A);E.configure(K,background=G,foreground=_A,font=(I,10,O));E.configure(P,background=H,foreground=_A,font=(I,10));E.configure(Q,fieldbackground=G,foreground=_A,background=G);E.map(K,background=[(J,_A),(_E,'#555555')],foreground=[(J,H),(_E,'#888888')]);E.map(P,background=[(J,G)],foreground=[(J,_A)]);E.map(Q,fieldbackground=[(J,G)],selectbackground=[(J,G)]);E.configure(R,background=H);F=Font(family=I,size=10);B=ttk.Frame(root,padding=10,style=R);B.grid(row=0,column=0,sticky='nsew');A.root.grid_columnconfigure(0,weight=1);A.root.grid_rowconfigure(0,weight=1);M=tk.Label(B,text=N,font=(I,16,O),fg=_A,bg=H,highlightthickness=2,highlightbackground=_A);M.grid(row=0,column=0,columnspan=3,pady=(0,15));ttk.Label(B,text='Chain Input Mode:').grid(row=1,column=0,padx=5,pady=5,sticky=D);A.chain_input_mode=tk.StringVar(value=_H);ttk.Radiobutton(B,text='Auto',value=_H,variable=A.chain_input_mode,command=A.toggle_chain_input_mode).grid(row=1,column=1,padx=5,pady=5,sticky=C);ttk.Radiobutton(B,text=S,value=T,variable=A.chain_input_mode,command=A.toggle_chain_input_mode).grid(row=1,column=1,padx=(100,5),pady=5,sticky=C);ttk.Label(B,text='Select Chain:').grid(row=2,column=0,padx=5,pady=5,sticky=D);A.chain_var=tk.StringVar();A.chain_dropdown=ttk.Combobox(B,textvariable=A.chain_var,width=47,state=_G,font=F);A.chains=load_chains();L=[A[_J]for A in A.chains];A.chain_dropdown['values']=L
		if L:A.chain_var.set(L[0])
		A.chain_dropdown.grid(row=2,column=1,padx=5,pady=5,sticky=C);A.chain_dropdown.bind('<<ComboboxSelected>>',lambda event:A.update_chain_fields());ttk.Label(B,text='RPC URL:').grid(row=3,column=0,padx=5,pady=5,sticky=D);A.rpc_entry=ttk.Entry(B,width=50,font=F);A.rpc_entry.grid(row=3,column=1,padx=5,pady=5,sticky=C);ttk.Label(B,text='Chain ID:').grid(row=4,column=0,padx=5,pady=5,sticky=D);A.chain_id_entry=ttk.Entry(B,width=10,font=F);A.chain_id_entry.grid(row=4,column=1,padx=5,pady=5,sticky=C);ttk.Label(B,text='Gas Price (Gwei):').grid(row=5,column=0,padx=5,pady=5,sticky=D);A.gas_price_entry=ttk.Entry(B,width=10,font=F);A.gas_price_entry.insert(0,'0.015');A.gas_price_entry.grid(row=5,column=1,padx=5,pady=5,sticky=C);ttk.Label(B,text='Amount to Send (ETH):').grid(row=6,column=0,padx=5,pady=5,sticky=D);A.amount_entry=ttk.Entry(B,width=10,font=F);A.amount_entry.insert(0,_O);A.amount_entry.grid(row=6,column=1,padx=5,pady=5,sticky=C);ttk.Label(B,text='Sender Private Key:').grid(row=7,column=0,padx=5,pady=5,sticky=D);A.private_key_entry=ttk.Entry(B,width=50,show='*',font=F);A.private_key_entry.grid(row=7,column=1,padx=5,pady=5,sticky=C);ttk.Label(B,text='Return Wallet Address:').grid(row=8,column=0,padx=5,pady=5,sticky=D);A.return_wallet_entry=ttk.Entry(B,width=50,font=F);A.return_wallet_entry.grid(row=8,column=1,padx=5,pady=5,sticky=C);ttk.Label(B,text='Receiver Input Mode:').grid(row=9,column=0,padx=5,pady=5,sticky=D);A.input_mode=tk.StringVar(value=_I);ttk.Radiobutton(B,text='File',value=_I,variable=A.input_mode,command=A.toggle_input_mode).grid(row=9,column=1,padx=5,pady=5,sticky=C);ttk.Radiobutton(B,text=S,value=T,variable=A.input_mode,command=A.toggle_input_mode).grid(row=9,column=1,padx=(100,5),pady=5,sticky=C);ttk.Label(B,text='Receiver File:').grid(row=10,column=0,padx=5,pady=5,sticky=D);A.file_entry=ttk.Entry(B,width=40,font=F);A.file_entry.grid(row=10,column=1,padx=5,pady=5,sticky=C);A.browse_button=ttk.Button(B,text='Browse',command=A.browse_file);A.browse_button.grid(row=10,column=2,padx=5,pady=5);ttk.Label(B,text='Manual Receivers (one per line):').grid(row=11,column=0,padx=5,pady=5,sticky=D);A.manual_entry=scrolledtext.ScrolledText(B,height=4,width=50,wrap=tk.WORD,bg=G,fg=_A,insertbackground=_A,font=F,borderwidth=2,relief=U,highlightthickness=1,highlightbackground=_A);A.manual_entry.grid(row=11,column=1,columnspan=2,padx=5,pady=5);A.manual_entry.insert(tk.END,_M);A.manual_entry.bind('<FocusIn>',lambda event:A.clear_placeholder());A.output_text=scrolledtext.ScrolledText(B,height=12,width=70,wrap=tk.WORD,bg=G,fg=_A,insertbackground=_A,font=F,borderwidth=2,relief=U,highlightthickness=1,highlightbackground=_A);A.output_text.grid(row=12,column=0,columnspan=3,padx=5,pady=10);A.status_label=tk.Label(B,text=_P,fg=_A,bg=H,font=(I,10,'italic'));A.status_label.grid(row=13,column=0,columnspan=3,pady=5);A.start_button=ttk.Button(B,text='Start Transactions',command=A.start_transactions,style=K);A.start_button.grid(row=14,column=0,padx=5,pady=5);A.clear_button=ttk.Button(B,text='Clear Inputs',command=A.clear_inputs,style=K);A.clear_button.grid(row=14,column=1,padx=5,pady=5);A.toggle_chain_input_mode();A.toggle_input_mode()
		if A.chains:A.update_chain_fields()
		A.glow_index=0;A.glow_colors=[_A,'#00cc00',_A];A.animate_title(M)
	def animate_title(A,title_label):B=title_label;B.configure(highlightbackground=A.glow_colors[A.glow_index]);A.glow_index=(A.glow_index+1)%len(A.glow_colors);A.root.after(500,A.animate_title,B)
	def browse_file(A):
		B=filedialog.askopenfilename(filetypes=[('Text files','*.txt'),('All files','*.*')])
		if B:A.file_entry.delete(0,tk.END);A.file_entry.insert(0,B)
	def clear_placeholder(A):
		if A.manual_entry.get(_K,tk.END).strip()==_M:A.manual_entry.delete(_K,tk.END)
	def update_chain_fields(A):
		'Update RPC URL and Chain ID fields based on selected chain'
		if A.chain_input_mode.get()==_H:
			B=next((B for B in A.chains if B[_J]==A.chain_var.get()),_F)
			if B:A.rpc_entry.configure(state=_C);A.rpc_entry.delete(0,tk.END);A.rpc_entry.insert(0,B['rpc']);A.rpc_entry.configure(state=_G);A.chain_id_entry.configure(state=_C);A.chain_id_entry.delete(0,tk.END);A.chain_id_entry.insert(0,str(B[_L]));A.chain_id_entry.configure(state=_G)
	def toggle_chain_input_mode(A):
		'Toggle between auto and manual chain input modes'
		if A.chain_input_mode.get()==_H:A.chain_dropdown.configure(state=_G);A.rpc_entry.configure(state=_G);A.chain_id_entry.configure(state=_G);A.update_chain_fields()
		else:A.chain_dropdown.configure(state=_E);A.rpc_entry.configure(state=_C);A.chain_id_entry.configure(state=_C)
	def toggle_input_mode(A):
		if A.input_mode.get()==_I:A.file_entry.configure(state=_C);A.browse_button.configure(state=_C);A.manual_entry.configure(state=_E)
		else:A.file_entry.configure(state=_E);A.browse_button.configure(state=_E);A.manual_entry.configure(state=_C)
	def clear_inputs(A):'Clear all input fields';A.chain_var.set(A.chains[0][_J]if A.chains else'');A.rpc_entry.configure(state=_C);A.rpc_entry.delete(0,tk.END);A.rpc_entry.insert(0,'https://base.llamarpc.com');A.chain_id_entry.configure(state=_C);A.chain_id_entry.delete(0,tk.END);A.chain_id_entry.insert(0,'8453');A.gas_price_entry.delete(0,tk.END);A.gas_price_entry.insert(0,'0.015');A.amount_entry.delete(0,tk.END);A.amount_entry.insert(0,_O);A.private_key_entry.delete(0,tk.END);A.return_wallet_entry.delete(0,tk.END);A.file_entry.delete(0,tk.END);A.manual_entry.delete(_K,tk.END);A.manual_entry.insert(tk.END,_M);A.output_text.delete(1.,tk.END);A.status_label.config(text=_P,fg=_A);A.start_button.state([_B]);A.toggle_chain_input_mode()
	def start_transactions(A):
		try:
			if A.chain_input_mode.get()==_H:
				B=next((B for B in A.chains if B[_J]==A.chain_var.get()),_F)
				if not B:messagebox.showerror(_D,'Selected chain not found.');return
				C=B['rpc'];D=B[_L]
			else:C=A.rpc_entry.get();D=int(A.chain_id_entry.get())
			E=float(A.gas_price_entry.get());F=float(A.amount_entry.get());G=A.private_key_entry.get();H=A.return_wallet_entry.get().strip();I=A.file_entry.get()if A.input_mode.get()==_I else A.manual_entry.get(_K,tk.END).strip();K=A.input_mode.get()==_I
			if not all([C,D,E,F,G,I,H]):messagebox.showerror(_D,'All fields must be filled.');return
			A.start_button.state([_E]);threading.Thread(target=run_transactions,args=(C,D,E,F,G,I,K,H,A.output_text,A.status_label,A.start_button),daemon=True).start()
		except ValueError as J:messagebox.showerror(_D,'Invalid input: Chain ID, Gas Price, and Amount must be numeric.');A.start_button.state([_B])
		except Exception as J:messagebox.showerror(_D,f"An error occurred: {str(J)}");A.start_button.state([_B])
if __name__=='__main__':root=tk.Tk();app=EthereumGUI(root);root.mainloop()
