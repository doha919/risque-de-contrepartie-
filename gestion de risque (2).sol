// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GestionnaireRisqueContrepartie {
    struct Contrepartie {
        address portefeuille;
        uint256 scoreCredit;
        uint256 limiteExposition;
        uint256 expositionLongue;
        uint256 expositionCourte;
        uint256 expositionCourante;
        uint256 collaterale;  // Nouveau champ pour le collatéral
        bool estActif;
    }

    // Variables d'état
    mapping(address => Contrepartie) public contreparties;
    mapping(address => mapping(address => uint256)) public expositions;

    // Événements
    event ContrepartieAjoutee(address indexed contrepartie, uint256 limiteExposition);
    event ExpositionMiseAJour(address indexed contrepartie, uint256 nouvelleExposition);
    event LimiteDepassee(address indexed contrepartie, uint256 exposition);

    // Ajouter une nouvelle contrepartie avec collatéral
    function ajouterContrepartie(address _portefeuille, uint256 _scoreCredit, uint256 _limiteExposition, uint256 _collaterale) public {
        require(contreparties[_portefeuille].portefeuille == address(0), "Contrepartie deja existee");
        
        contreparties[_portefeuille] = Contrepartie({
            portefeuille: _portefeuille,
            scoreCredit: _scoreCredit,
            limiteExposition: _limiteExposition,
            expositionLongue: 0,
            expositionCourte: 0,
            expositionCourante: 0,
            collaterale: _collaterale,
            estActif: true
        });

        emit ContrepartieAjoutee(_portefeuille, _limiteExposition);
    }

    // Mettre à jour l'exposition d'une contrepartie (longue ou courte)
    function mettreAJourExposition(address _portefeuille, uint256 _nouvelleExposition, bool estLongue) public {
        Contrepartie storage contrepartie = contreparties[_portefeuille];
        require(contrepartie.portefeuille != address(0), "Contrepartie inexistante");
        require(contrepartie.estActif, "Contrepartie inactive");

        if (estLongue) {
            contrepartie.expositionLongue += _nouvelleExposition;
        } else {
            contrepartie.expositionCourte += _nouvelleExposition;
        }
        
        // Calcul de l'exposition nette
        contrepartie.expositionCourante = contrepartie.expositionLongue - contrepartie.expositionCourte;

        // Vérifier si la limite est dépassée
        if (contrepartie.expositionCourante > contrepartie.limiteExposition) {
            emit LimiteDepassee(_portefeuille, contrepartie.expositionCourante);
        }

        emit ExpositionMiseAJour(_portefeuille, contrepartie.expositionCourante);
    }

    // Calculer le risque d'une contrepartie (Exposition Courante / Limite d’Exposition) * 100 * Score de Crédit
    function calculerRisque(address _portefeuille) public view returns (uint256) {
        Contrepartie storage contrepartie = contreparties[_portefeuille];
        require(contrepartie.portefeuille != address(0), "Contrepartie inexistante");

        if (contrepartie.limiteExposition == 0) {
            return 0;
        }
        
        // Calcul du risque basé sur l'exposition et la limite
        uint256 risque = (contrepartie.expositionCourante * 100 * contrepartie.scoreCredit) / contrepartie.limiteExposition;
        return risque;
    }

    // Calculer le Ratio de Couverture (collatéral / exposition totale)
    function calculerRatioCouverture(address _portefeuille) public view returns (uint256) {
        Contrepartie storage contrepartie = contreparties[_portefeuille];
        require(contrepartie.portefeuille != address(0), "Contrepartie inexistante");

        if (contrepartie.expositionCourante == 0) {
            return 0;
        }

        // Calcul du ratio de couverture
        uint256 ratio = (contrepartie.collaterale * 100) / contrepartie.expositionCourante;
        return ratio;
    }

    // Désactiver une contrepartie
    function desactiverContrepartie(address _portefeuille) public {
        Contrepartie storage contrepartie = contreparties[_portefeuille];
        require(contrepartie.portefeuille != address(0), "Contrepartie inexistante");
        contrepartie.estActif = false;
    }
}