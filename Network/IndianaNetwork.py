import numpy as np

from .BaseNetwork import *

class IndianaNetwork(BaseNetwork):
    
    def __init__(self,
                file_name,
                n_assets,
                is_deck = True,
                is_superstructure = True,
                is_substructure = True):
        super().__init__(file_name, n_assets)
        
    def load_asset(self, idx = 0):
        
        asset_info = self.assets_df.loc[idx, :]
        
        id_, length, width, material, design = asset_info[0:5]
        vertical_clearance = asset_info[21]
        asset = Bridge(ID = id_, length = length,
                                width = width,
                                material = material,
                                design = design,
                                vertical_clearance = vertical_clearance)
        asset.set_accumulator(Accumulator)

        # Setting traffic info
        road_class, ADT, truck_percentage, detour_length = asset_info[5:9]
        asset.set_traffic_info(road_class = road_class, ADT = ADT, truck_percentage = truck_percentage, detour_length = detour_length)
        
        # Setting seismic info
        hazus_class, site_class, skew_angle, n_spans = asset_info[9:13]
        asset.set_seismic_info(hazus_class = hazus_class, site_class = site_class, skew_angle = skew_angle, n_spans = n_spans)
        
        # Setting MRR durations and effectiveness models
        maint_duration, rehab_duration, recon_duration = asset_info[13:16]
        mrr = MRRFourActions(maint_duration = maint_duration, rehab_duration = rehab_duration, recon_duration = recon_duration)
        mrr.set_effectiveness(SimpleEffectiveness())
        asset.set_mrr_model(mrr)

        # User cost model
        asset.set_user_cost_model(TexasDOTUserCost())
        
        # Hazard models
        hazard_model = HazardModel()
        hazard_model.set_asset(asset)
        "Only earthquakes with magnitude of 4 or higher and based on historical data from USGS"
        hazard_model.set_generator_model(PoissonProcess(occurrence_rate = 0.3, dist = Exponential(2.1739, 4))) 
        hazard_model.set_response_model(HazusBridgeResponse(asset))
        hazard_model.set_loss_model(HazusLoss())
        hazard_model.set_recovery_model(SimpleRecovery())
        asset.set_hazard_model(hazard_model)
        asset.set_replacement_value_model(hazus_default = True)
        
        # Finding the age
        age = asset_info [16]

        if is_deck:
            # Adding the deck to the asset
            deck_material, deck_cond = asset_info [17:19]
            deck = BridgeElement(name = DECK,
                                initial_condition = min(9-deck_cond, 7),
                                age = age,
                                material = deck_material)
            deck.set_asset(asset)
            deck.set_condition_rating_model(NBI())
            deck.set_deterioration_model(Markovian())
            deck.set_utility_model(DeckUtility())
            deck.set_agency_costs_model(DeckCosts())
            asset.add_element(deck)

        if is_superstructure:
            # Adding the superstructure to the asset
            superstructure_cond = asset_info [19]
            superstructure = BridgeElement(name = SUPERSTRUCTURE,
                                            initial_condition = min(9-superstructure_cond, 7),
                                            age = age)
            superstructure.set_asset(asset)
            superstructure.set_condition_rating_model(NBI())
            superstructure.set_deterioration_model(Markovian())
            superstructure.set_utility_model(SuperstructureUtility())
            superstructure.set_agency_costs_model(SuperstructureCosts())
            asset.add_element(superstructure)

        if is_substructure:
            # Adding the substruture to the asset
            substructure_cond = asset_info[20]
            substructure = BridgeElement(name = SUBSTRUCTURE,
                                        initial_condition = min(9-substructure_cond,7),
                                        age = age)
            substructure.set_asset(asset)
            substructure.set_condition_rating_model(NBI())
            substructure.set_deterioration_model(Markovian())
            substructure.set_utility_model(SubstructureUtility())
            substructure.set_agency_costs_model(SubstructureCosts())
            asset.add_element(substructure)
 
        return asset
    
    def load_network(self):
        
        self.assets = []
        for idx in self.assets_df.index:
            assets.append(self.load_asset(idx))

        return self.assets

    def set_current_budget_limit(self, val):
        self.current_budget_limit = val

    def set_budget_limit_model(self, model):
        self.budget_model = model
        
    def set_npv_budget_limit(self, val):
        self.npv_budget_limit = val

    def objective1(self):
        return np.random.random()

    def objective2(self):
        return np.random.random()
