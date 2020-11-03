- Protocolo de replicação baseado em cópia primária
	- Escrita local
	- Versão simplificada

- Cenário com 4 réplicas permanentes
	- A cópia primária migra entre as réplicas que querem escrever (troca de chapéu)
	- Só quem tem o chapéu pode escrever
	- Quero alterar o dado?
		- Acho a cópia primária
		- Pego o chapéu pra mim
		- Mudo o valor
		- Propago as mudanças para as outras réplicas

- Dado a ser replicado: variável inteira X (valor inicial = 0)
	- Réplicas vão manter um histórico de atualizações realizadas no dado 
		- Par (id da réplica que mudou, novo valor)
		- Se uma réplica muda várias vezes mas só passa o valor final, o histórico tem que constar TODAS as mudanças

- Implementação
	- Um único programa que vai ser rodado por todas as réplicas
	- Entrada: ID da réplica
	- Vai oferecer para o usuário uma interface de acesso que nos deixa:
		- Ler o valor de X na réplica
		- Ler o histórico de alterações de X
		- Alterar o valor de X
		- Terminar o programa
