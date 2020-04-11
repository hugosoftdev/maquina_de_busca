# Projeto Máquina de busca

#### Dupla: Hugo e Jean

Olá Ayres! Neste Readme vamos descrever o que a nossa
search engine tem  de diferente do que fizemos em aula!

## Entedimento da Query

Diferentemente do que fizemos em aula, a intenção não era criar uma maquina de busca para queries booleanas, e sim parsear uma query "livre", ou seja, o usuário escreve o que quiser e o algoritmo por trás tenta entender minimamente a inteção de busca.

A maior limitação do que foi desenvolvido em aula era que cada token continha apenas uma palavra, "New York" era separado em `['New','York']`, o que queríamos era dar um jeito de deixar essa identificação de tokens mais robusta.
O que fizemos foi adicionar ao entendimento da query dois novos conceitos.

-   Elementos Pricipais
-   Elementos Interessantes

Nem tudo que é escrito numa pesquisa tem a mesma relevância, seria bom se conseguíssemos identificar quais os principais termos da pesquisa e ao mesmo tempo fôssemos capaz de tokeniza-los de uma maneira mais inteligente. Para isso, envolvemos <strong>NER (Named Entity Recognition) e POS (Part-of-speech) tagging </strong>. Considere a seguinte 
frase:

"How to get to that beautiful street in New York"

Utilizando o modelo de NER do <strong>spaCy</strong> identifica-se o elemento "New York", e neste caso vamos destaca-lo como o principal elemento da pesquisa. Mas ainda há outras informações relevantes no texto. Classificamos a seguinte "relevância" para algumas classes gramáticais:

- Substantivo -> 2
- Verbo -> 2
- Adjetivo -> 1
- Advérbio -> 1

Com base na premissa de que as principais informações da pesquisa concentram-se nos substantivos e nos verbos, e em sequencia nos advérbios e adjetivos. Então neste caso o parsing dessa query nos retornaria a seguinte estrutura:

Main Elements: "New York"

Intersting Elements: ("street",2), ("get",2), ("beautiful",1), ("how",1)

Agora temos os principais elementos da pesquisa acompanhados de seus respectivos pesos, isso será importante mais para frente na hora do ranking dos resultados. Caso o algortimo de NER não ache nenhuma entidade, o que é considerado como Main Elements são os substantivos e verbos, e caso o modelo de POS não ache nenhum substantivo ou verbo no texto o main elements se torna um simples `word_tokenize` da query, ou seja, se não conseguimos entender o que são os principais elementos, vamos assumir que todos são igualmente importantes.

### Criação do Repositório e do Index

Assim como no entendimento da query, construímos em aula um repositório e index que consideravam as palavras de forma individual, se quiséssemos buscar pelos documentos com o termo "New York" teríamos que buscar isoladamente no index as chaves "New" e "York" e ainda salvar junto a informação de cada documento em qual index aquela palavra apareceu para enfim sabermos se era o termo "New York". Assim como no entendimento da query, decimos aplicar <strong>NER</strong>
para resolver este problema. Além de fazermos o `word_tokenize` do conteúdo de cada documento na hora de construírmos o repositório, adicionamos também quais as principais entidades de nome composto que foram reconhecidas no texto entre a lista de tokens. Veja abaixo:

O repositório do corpus:

   ` {
        "docid2": "New York"
    }
    `

seria:
    ` {
        "docid2": ['New','York','New York']
    }
    `

E como mantivémos a lógica da criação do Index, por consequencia o index seria:
`{
    "New": ['docid2'],
    "York": ['docid2'],
    "New York": ['docid2']
}
`

Ou seja, resolvemos o problema indexando também os termos compostos de maior interesse! A criação do Repositório torna-se mais demorada pela identificação desses termos pelo modelo de NER, mas a vantagem de perfomance por indexa-los é muito maior! O usuário agradece.


### Correção automática

As vezes na pressa acabamos por escrever alguns termos errados na pesquisa, ou mesmo por não sabermos ao certo como escreve-los colocamos uma "aproximação" do que seria a palavra. Com base nos mains elements identificados no entendimento de query, iteramos pelas chaves no index para sabermos se aquele termo ja apareceu no corpus em algum momento. Caso não, utilizamos o algoritmo da <strong>distância de Levenshtein </strong> para escolher o termo indexado mais próximo do termo que você pesquisou. A distância máxima para o termo ser considerado uma sugestão válida foi definida como 3 pela dupla.

Exemplificando, a pesquisa:

    From where it is Bank off Amerika

Vem acompanhada da sugestão:

    Did you meant: "From where it is Bank of America"?

Caso você selecione sim, o programa passa a considerar que a query inicial é igual à query sugerida, caso selecione não continua-se a busca com a query inicial.

O diferencial de ter construído um index com algumas entidades de nome composto também surte efeito nessa sugestão, <strong> pois a sugestão passa a ser a correção do termo e não de cada palavra isoladamente </strong>.

### Busca e Ranking

A busca em si dos documentos sucetíveis a ranqueamento
é bem simples, só serão selecionados os documentos que tiverem
os termos dentro da estrutura Main Elements, se o documento 
não tiver todos elementos tidos como principais dentro da pesquisa ele não é considerado. Uma vez esses documentos tendo sido selecionados chega enfim a última fase, a fase de ranqueamento dos resultados.

Para dar um score a cada um dos documentos vamos utilizar tanto os Main Elements quanto finalmente os Intersting Elements identificados la no entedimento da query. Para isso, criamos a seguinte regra de score:

- Para cada termo principal, o documento ganha um score de 3 pontos para cada ocorrência desse elemento.
- Para cada termo interessante, o documento ganha um score  de 1 ponto para cada ocorrência vezes o peso de relevância daquele termo.

Ao final, retornamos para o usuário os 3 (ou menos) documentos de maior pontuação, encerrando assim a pesquisa.

### Rodando o projeto

Dependências:
- python 3.5 ou maior
- spaCy
- nltk
- python-Levenshtein


Ordem de execução dos scripts:

    $ python corpus_creator.py

    $ python repo_and_index.creator.py

    $ python searcher.py

### Considerações

O campo de máquina de busca é simplesmente um universo gigantesco cheio de técnicas para serem estudadas. Muitas melhorias poderiam ser aplicadas nesse projeto, mas desenvolvemos o que foi possível dentro do prazo estipulado alcançando um resultado satisfatório para dupla. A intenção é que seja um script genérico e que funcione para QUALQUER CORPUS, desde que seguindo a estrutura do corpus utilizado neste projeto. Como melhoria de uso do programa em si, colocaríamos como um próximo passo tornar o nome dos arquivos do corpus, index e repositório argumentos da linha de comando, assim como a quantidade máxima de resultado a serem retornados na busca. Por hora, isso deve ser alterado dentro do código.


### Happy Searching!!

---