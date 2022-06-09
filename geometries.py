
def geometry_def(geo_name):

    H2 = {"schema": "molecular_geometry",
            "sites": [
                        {"species": "H","x": 0,"y": 0,"z": 0},
                        {"species": "H","x": 0,"y": 0,"z": 0.7},
                        ]
            } 
    H4 = {"schema": "molecular_geometry",
                "sites": [
                            {"species": "H","x": 0,"y": 0,"z": 0},
                            {"species": "H","x": 0,"y": 0,"z": 0.75},
                            {"species": "H","x": 0.75,"y": 0,"z": 0.0},
                            {"species": "H","x": 0.75,"y": 0,"z": 0.75},
                         ]
          }
    Li = {"schema": "molecular_geometry",
            "sites": [
                        {"species": "Li","x": 0,"y": 0,"z": 0},
                     ]
                }

    geo_dict = {"h2": H2, "h4": H4, "li": Li} 
    return geo_dict[geo_name]      
