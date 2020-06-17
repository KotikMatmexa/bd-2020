package rx

import io.reactivex.rxjava3.core.Flowable
import io.reactivex.rxjava3.schedulers.Schedulers
import kotlinx.coroutines.*
import java.io.File
import java.math.BigInteger
import java.nio.file.Files
import java.nio.file.Paths
import java.util.*
import kotlin.collections.ArrayList

//Генерация данных
fun generate(FileName: String, Range: Int, BitBound: Int){
    val ListInts = ArrayList<BigInteger>()
    val rand = Random()
    for (i in (1..Range)) {
        ListInts.add(BigInteger(BitBound, rand))
    }
    File(FileName).writeText(ListInts.joinToString("\n"))
}
//Основной скрипт для факторизции
fun tdFactors(n: BigInteger): LinkedList<BigInteger>? {
    var n = n
    val two = BigInteger.valueOf(2)
    val fs: LinkedList<BigInteger> = LinkedList<BigInteger>()
    require(n.compareTo(two) >= 0) { "must be greater than one" }
    while (n.mod(two) == BigInteger.ZERO) {
        fs.add(two)
        n = n.divide(two)
    }
    if (n.compareTo(BigInteger.ONE) > 0) {
        var f = BigInteger.valueOf(3)
        while (f.multiply(f).compareTo(n) <= 0) {
            if (n.mod(f) == BigInteger.ZERO) {
                fs.add(f)
                n = n.divide(f)
            } else {
                f = f.add(two)
            }
        }
        fs.add(n)
    }
    return fs
}
//Последовательный подсчет
fun sequence(values:List<BigInteger>): Int{
    val resultList: ArrayList<BigInteger> = ArrayList<BigInteger>()
    for (item in values) {
        val result = tdFactors(item)
        if (result != null) {
            for (k in result){
                resultList.add(k)
            }
        }
    }
    val unique: Set<BigInteger> = HashSet<BigInteger>(resultList)
    return unique.size
}


fun main(){
    //Генерация данных
    generate("KotlinNumbers.txt",2000,32)
    val allLines: List<String>  = Files.readAllLines(Paths.get("KotlinNumbers.txt"))
    val intList = ArrayList<BigInteger>()
    for (s in allLines) intList.add(BigInteger(s))
    val tStart = System.currentTimeMillis()
    println(sequence(intList))
    val tEnd = System.currentTimeMillis()
    val tDelta = tEnd - tStart
    println(tDelta)


    //Параллельный подсчет с помощью RxJava
    val sStart = System.currentTimeMillis()
    val vals = Flowable.fromIterable(intList)
    var res = ArrayList<LinkedList<BigInteger>>()
    vals.parallel()
        .runOn(Schedulers.computation())
        .map<LinkedList<BigInteger>> { i: BigInteger -> tdFactors(i) }
        .sequential()
        .subscribe { v: LinkedList<BigInteger> -> res.add(v) }
    var reslist = ArrayList<BigInteger>()
    for (line in res) {
        for (item in line){
            reslist.add(item)
        }
    }
    println(HashSet<BigInteger>(reslist).size)
    val sEnd = System.currentTimeMillis()
    val sDelta = sEnd - sStart
    println(sDelta)


    //Параллельный подсчет с помощью примитивов синхронизации (async)

    var res2 = ArrayList<LinkedList<BigInteger>?>()
    val sStart2 = System.currentTimeMillis()
    var listsyncs = ArrayList<Deferred<LinkedList<BigInteger>?>>()
    for (i in intList){
        listsyncs.add(GlobalScope.async(){ tdFactors(i)})
    }
    runBlocking {for (k in listsyncs){(res2.add(k.await()))} }

    var reslist2 = ArrayList<BigInteger>()
    for (line in res2) {
        if (line != null) {
            for (item in line){
                reslist2.add(item)
            }
        }
    }
    println(HashSet<BigInteger>(reslist2).size)
    val sEnd2 = System.currentTimeMillis()
    val sDelta2 = sEnd2 - sStart2
    println(sDelta2)
}