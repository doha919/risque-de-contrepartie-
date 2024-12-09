import streamlit as st
from web3 import Web3
import json

# Initialisation de la connexion à l'interface blockchain
st.title("Gestionnaire de Risque de Contrepartie")

# Connexion au réseau local ou distant Ethereum (par exemple, Ganache, Infura, ou autre)
infura_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(infura_url))

if web3.is_connected():
    st.success("Connecté à Ethereum avec succès!")
else:
    st.error("Connexion au réseau Ethereum échouée. Vérifiez l'URL du noeud.")

# Adresse et ABI du smart contract
contract_address = "0x668BE9932D93bA35B6Adc7A1CFd7EB6223915fC3"
abi = [
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "contrepartie",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "limiteExposition",
				"type": "uint256"
			}
		],
		"name": "ContrepartieAjoutee",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "contrepartie",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "nouvelleExposition",
				"type": "uint256"
			}
		],
		"name": "ExpositionMiseAJour",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "contrepartie",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "exposition",
				"type": "uint256"
			}
		],
		"name": "LimiteDepassee",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_portefeuille",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "_scoreCredit",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_limiteExposition",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_collaterale",
				"type": "uint256"
			}
		],
		"name": "ajouterContrepartie",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_portefeuille",
				"type": "address"
			}
		],
		"name": "calculerRatioCouverture",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_portefeuille",
				"type": "address"
			}
		],
		"name": "calculerRisque",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "contreparties",
		"outputs": [
			{
				"internalType": "address",
				"name": "portefeuille",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "scoreCredit",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "limiteExposition",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "expositionLongue",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "expositionCourte",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "expositionCourante",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "collaterale",
				"type": "uint256"
			},
			{
				"internalType": "bool",
				"name": "estActif",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_portefeuille",
				"type": "address"
			}
		],
		"name": "desactiverContrepartie",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "expositions",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_portefeuille",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "_nouvelleExposition",
				"type": "uint256"
			},
			{
				"internalType": "bool",
				"name": "estLongue",
				"type": "bool"
			}
		],
		"name": "mettreAJourExposition",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]

# Variable globale pour stocker le contrat
if "contract" not in st.session_state:
    st.session_state.contract = None

if st.button("Charger le contrat"):
    try:
        st.session_state.contract = web3.eth.contract(address=contract_address, abi=abi)
        st.success("Contrat chargé avec succès!")
    except Exception as e:
        st.error(f"Erreur lors du chargement du contrat: {e}")

# Connexion avec MetaMask
user_address = st.text_input("Votre adresse Ethereum (MetaMask):", key="user_address")
if st.button("Vérifier adresse", key="verify_address"):
    if web3.is_address(user_address):
        st.success(f"Adresse valide: {user_address}")
    else:
        st.error("Adresse Ethereum invalide")

# Ajouter une nouvelle contrepartie
st.header("Ajouter une contrepartie")
new_address = st.text_input("Adresse de la contrepartie:", key="new_address")
score_credit = st.number_input("Score de crédit:", min_value=0, max_value=1000, step=1, key="score_credit")
limite_exposition = st.number_input("Limite d'exposition:", min_value=0, step=1, key="limite_exposition")
collaterale = st.number_input("Collatéral:", min_value=0, step=1, key="collaterale")

if st.button("Ajouter contrepartie", key="add_counterparty"):
    if st.session_state.contract:
        try:
            tx = st.session_state.contract.functions.ajouterContrepartie(
                new_address, score_credit, limite_exposition, collaterale
            ).transact({
                'from': user_address,
                'gas': 3000000,
                'gasPrice': web3.eth.gas_price
            })

            st.write("Transaction envoyée. Hash: ", web3.toHex(tx))
        except Exception as e:
            st.error(f"Erreur: {e}")
    else:
        st.error("Le contrat n'est pas chargé. Cliquez sur 'Charger le contrat'.")

# Mettre à jour l'exposition
st.header("Mettre à jour l'exposition")
update_address = st.text_input("Adresse de la contrepartie à mettre à jour:", key="update_address")
nouvelle_exposition = st.number_input("Nouvelle exposition:", min_value=0, step=1, key="nouvelle_exposition")
exposition_longue = st.radio("Type d'exposition:", ("Longue", "Courte"), key="exposition_type")

if st.button("Mettre à jour exposition", key="update_exposure"):
    if st.session_state.contract:
        try:
            est_longue = exposition_longue == "Longue"
            tx = st.session_state.contract.functions.mettreAJourExposition(
                update_address, nouvelle_exposition, est_longue
            ).transact({
                'from': user_address,
                'gas': 3000000,
                'gasPrice': web3.eth.gas_price
            })

            st.write("Transaction envoyée. Hash: ", web3.toHex(tx))
        except Exception as e:
            st.error(f"Erreur: {e}")
    else:
        st.error("Le contrat n'est pas chargé. Cliquez sur 'Charger le contrat'.")

# Calculer le risque
st.header("Calculer le risque")
risque_address = st.text_input("Adresse de la contrepartie à calculer:", key="risque_address")
if st.button("Calculer risque", key="calculate_risk"):
    if st.session_state.contract:
        try:
            risque = st.session_state.contract.functions.calculerRisque(risque_address).call()
            st.success(f"Le risque calculé est: {risque}")
        except Exception as e:
            st.error(f"Erreur: {e}")
    else:
        st.error("Le contrat n'est pas chargé. Cliquez sur 'Charger le contrat'.")

# Calculer le ratio de couverture
st.header("Calculer le ratio de couverture")
couverture_address = st.text_input("Adresse de la contrepartie à calculer:", key="couverture_address")
if st.button("Calculer ratio de couverture", key="calculate_ratio"):
    if st.session_state.contract:
        try:
            ratio = st.session_state.contract.functions.calculerRatioCouverture(couverture_address).call()
            st.success(f"Le ratio de couverture est: {ratio}%")
        except Exception as e:
            st.error(f"Erreur: {e}")
    else:
        st.error("Le contrat n'est pas chargé. Cliquez sur 'Charger le contrat'.")
