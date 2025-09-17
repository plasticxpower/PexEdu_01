export type AnimalGroup = 'mammals' | 'fish' | 'amphibians' | 'reptiles' | 'birds';

export interface AnimalEntry {
  id: string;
  group: AnimalGroup;
  commonName: string;
  scientificName: string;
  size: string;
  lifeExpectancy: string;
  habitat: string;
  funFact: string;
  image: string;
}

export interface GameSettings {
  group: AnimalGroup;
  gridSize: 12 | 18 | 24;
}

export interface CardData {
  id: string;
  animalId: string;
  revealed: boolean;
  matched: boolean;
}
