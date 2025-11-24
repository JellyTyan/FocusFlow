// Podstawowe przedmioty domyślnie
export const DEFAULT_SUBJECTS = [
  'Matematyka',
  'Fizyka',
  'Chemia',
  'Biologia',
  'Historia',
  'Geografia',
  'Język polski',
  'Literatura',
  'Język angielski',
  'Wiedza o społeczeństwie',
  'Informatyka',
  'Ekonomia',
  'Prawo',
  'Filozofia',
  'Psychologia',
  'Medycyna',
  'Inżynieria',
  'Design',
  'Inne',
];

export function getSubjectOptions(savedSubjects: Array<{ name: string }>): string[] {
  if (!Array.isArray(savedSubjects)) {
    return [...DEFAULT_SUBJECTS];
  }
  
  const allSubjects = [...DEFAULT_SUBJECTS];
  
  // Dodajemy zapisane przedmioty, których nie ma w podstawowych
  savedSubjects.forEach(subject => {
    if (!DEFAULT_SUBJECTS.includes(subject.name)) {
      allSubjects.push(subject.name);
    }
  });
  
  return allSubjects;
}

